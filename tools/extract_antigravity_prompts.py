#!/usr/bin/env python3
"""
Extract and analyze user prompts from Antigravity conversation .pb files.

This script decodes Protocol Buffer files from Antigravity's conversations folder
and extracts user prompts for metacognition practice and prompt improvement.

Features:
  - Direct reading from Antigravity .pb conversation files
  - Prompt categorization (command, question, clarification, feedback, etc.)
  - Statistics and pattern analysis
  - Training-focused output format

Usage:
    python extract_antigravity_prompts.py                    # Process most recent
    python extract_antigravity_prompts.py <conversation_id>  # Specific conversation
    python extract_antigravity_prompts.py --list             # List all conversations
    python extract_antigravity_prompts.py --all --analyze    # All with analysis
    python extract_antigravity_prompts.py --stats            # Statistics only
    python extract_antigravity_prompts.py --training         # Training format
"""

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Generator


# ============================================================================
# Constants
# ============================================================================

DEFAULT_CONVERSATIONS_PATH = Path.home() / ".gemini" / "antigravity" / "conversations"


# ============================================================================
# Categories and Patterns
# ============================================================================

class PromptCategory:
    """Categories for user prompts."""
    COMMAND = "command"
    QUESTION = "question"
    CLARIFICATION = "clarification"
    FEEDBACK = "feedback"
    CONTEXT = "context"
    CORRECTION = "correction"
    CONTINUATION = "continuation"
    OTHER = "other"


IMPERATIVE_VERBS = {
    'create', 'make', 'build', 'generate', 'write', 'add', 'implement',
    'fix', 'repair', 'solve', 'resolve', 'debug', 'patch',
    'update', 'modify', 'change', 'edit', 'adjust', 'refactor',
    'remove', 'delete', 'clear', 'clean', 'strip',
    'explain', 'describe', 'show', 'display', 'list', 'print',
    'find', 'search', 'locate', 'look', 'check', 'verify', 'validate',
    'run', 'execute', 'test', 'try', 'start', 'stop',
    'save', 'export', 'import', 'load', 'read', 'parse', 'extract',
    'review', 'analyze', 'inspect', 'investigate', 'research',
    'help', 'assist', 'guide', 'teach', 'learn',
    'install', 'setup', 'configure', 'deploy', 'publish',
    'document', 'comment', 'annotate', 'note',
    'convert', 'transform', 'translate', 'format',
    'copy', 'move', 'rename', 'organize',
    'compare', 'diff', 'merge', 'split', 'combine',
    'enhance', 'improve', 'optimize', 'simplify',
}

QUESTION_PATTERNS = [
    r'\?$',
    r'^(what|why|how|when|where|which|who|whose|whom|can|could|would|should|is|are|do|does|did|will|has|have)\b',
    r'^(tell me|show me|explain)\b',
]

CORRECTION_PATTERNS = [
    r'^(no,?\s+|actually|wait|hold)',
    r'^(that\'s not|not quite|incorrect)',
    r'^(i meant|i mean|what i meant)',
]

FEEDBACK_PATTERNS = [
    r'^(this (is|looks|works)|that (is|looks|works))',
    r'^(good|great|perfect|excellent|nice|awesome)',
    r'^(the issue is|the problem is|it\'s (not|still))',
]

CONTEXT_PATTERNS = [
    r'^(here\'s|here is|for context|fyi|note that|keep in mind)',
    r'^(i\'m (trying|working|using)|we (are|have|need))',
    r'@\[[^\]]+\]',
]


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ExtractedPrompt:
    """Represents an extracted user prompt with metadata."""
    content: str
    byte_offset: int = 0
    length: int = 0
    word_count: int = 0
    category: str = PromptCategory.OTHER
    file_references: list[str] = field(default_factory=list)
    has_code_block: bool = False
    imperative_verbs: list[str] = field(default_factory=list)
    source_file: str = ""


@dataclass
class PromptStats:
    """Statistics about extracted prompts."""
    total_prompts: int = 0
    total_words: int = 0
    avg_words: float = 0.0
    category_counts: dict[str, int] = field(default_factory=dict)
    common_verbs: list[tuple[str, int]] = field(default_factory=list)
    common_patterns: list[tuple[str, int]] = field(default_factory=list)
    word_count_distribution: dict[str, int] = field(default_factory=dict)
    files_processed: int = 0


# ============================================================================
# Classification Functions
# ============================================================================

def classify_prompt(content: str) -> str:
    """Classify a prompt into a category."""
    content_lower = content.lower().strip()

    if re.match(r'^(continue|proceed|go ahead|go on|next)\.?$', content_lower):
        return PromptCategory.CONTINUATION

    for pattern in CORRECTION_PATTERNS:
        if re.search(pattern, content_lower):
            return PromptCategory.CORRECTION

    for pattern in FEEDBACK_PATTERNS:
        if re.search(pattern, content_lower):
            return PromptCategory.FEEDBACK

    for pattern in QUESTION_PATTERNS:
        if re.search(pattern, content_lower):
            return PromptCategory.QUESTION

    for pattern in CONTEXT_PATTERNS:
        if re.search(pattern, content_lower):
            return PromptCategory.CONTEXT

    first_word = content_lower.split()[0].rstrip('.,!?:') if content_lower.split() else ''
    if first_word in IMPERATIVE_VERBS:
        return PromptCategory.COMMAND

    words = set(re.findall(r'\b\w+\b', content_lower))
    if words & IMPERATIVE_VERBS:
        return PromptCategory.COMMAND

    return PromptCategory.OTHER


def extract_imperative_verbs(content: str) -> list[str]:
    """Extract imperative verbs from prompt content."""
    words = re.findall(r'\b\w+\b', content.lower())
    return [w for w in words if w in IMPERATIVE_VERBS]


def extract_file_references(content: str) -> list[str]:
    """Extract @[file] references from content."""
    return re.findall(r'@\[([^\]]+)\]', content)


def has_code_block(content: str) -> bool:
    """Check if content contains a code block."""
    return '```' in content or content.count('`') >= 2


# ============================================================================
# Binary Extraction Functions
# ============================================================================

def find_text_strings(data: bytes, min_length: int = 20) -> Generator[tuple[str, int], None, None]:
    """Extract readable text strings from binary protobuf data."""
    i = 0
    while i < len(data) - min_length:
        start = i
        text_chars = []

        while i < len(data):
            byte = data[i]
            if 32 <= byte < 127 or byte in (9, 10, 13):
                text_chars.append(chr(byte))
                i += 1
            elif byte >= 128:
                try:
                    remaining = data[i:i+4]
                    char = remaining.decode('utf-8', errors='strict')[:1]
                    if char and char.isprintable():
                        text_chars.append(char)
                        i += len(char.encode('utf-8'))
                    else:
                        break
                except:
                    break
            else:
                break

        text = ''.join(text_chars)
        if len(text) >= min_length:
            yield (text, start)

        i = max(i, start + 1)


def is_likely_user_prompt(text: str) -> bool:
    """Heuristically determine if a text string is likely a user prompt."""
    text = text.strip()

    if len(text) < 10:
        return False

    code_patterns = [
        r'^(import |from |def |class |function |const |let |var |async |await )',
        r'^[{}\[\]<>]',
        r'^(https?://|file://|/[a-z])',
        r'^\d+\.\d+\.\d+',
        r'^[A-Z_]{3,}=',
    ]

    for pattern in code_patterns:
        if re.match(pattern, text, re.IGNORECASE):
            return False

    alpha_ratio = sum(1 for c in text if c.isalpha()) / len(text)
    if alpha_ratio < 0.4:
        return False

    ai_patterns = [
        r'^(I\'ll |Let me |I can |I will |Here\'s |Based on |To |The |This )',
        r'^(Now |Perfect|Great|Good|Excellent|Done|OK|Okay)',
        r'^\*\*',
        r'^```',
        r'^Step \d+:',
    ]

    for pattern in ai_patterns:
        if re.match(pattern, text, re.IGNORECASE):
            return False

    user_indicators = [
        r'(please|can you|could you|would you|help me|i want|i need|create|make|build|fix|update|add|remove|change|modify|explain|show|tell|find|search|look|check|verify|test|run|execute)',
        r'\?$',
        r'^@\[',
    ]

    for pattern in user_indicators:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    first_word = text.split()[0].lower().rstrip('.,!?:')
    if first_word in IMPERATIVE_VERBS:
        return True

    return False


def is_trivial_prompt(text: str) -> bool:
    """Check if a prompt is trivial (should be filtered out)."""
    text = text.strip().lower()

    trivial = {
        'continue', 'proceed', 'yes', 'no', 'ok', 'okay', 'sure', 'thanks',
        'thank you', 'got it', 'sounds good', 'perfect', 'great', 'good',
        'next', 'go ahead', 'go on', 'done', 'stop', 'wait', 'pause',
        'y', 'n', 'k', 'lgtm', 'wfm', 'ack', 'fixed', 'approved',
        '1', '2', '3', '4', '5', 'a', 'b', 'c'
    }

    if text.rstrip('.!?') in trivial:
        return True

    if len(text.split()) < 3 and len(text) < 20:
        return True

    return False


# ============================================================================
# Extraction Functions
# ============================================================================

def extract_prompts_from_pb(
    pb_path: Path,
    include_trivial: bool = False,
    source_file: str = ""
) -> list[ExtractedPrompt]:
    """Extract user prompts from a .pb conversation file."""
    with open(pb_path, 'rb') as f:
        data = f.read()

    prompts = []
    seen = set()

    for text, offset in find_text_strings(data, min_length=15):
        text = text.strip()

        if text in seen:
            continue
        seen.add(text)

        if is_likely_user_prompt(text):
            if include_trivial or not is_trivial_prompt(text):
                content_for_word_count = re.sub(r'@\[[^\]]+\]', '', text)
                word_count = len(content_for_word_count.split())

                prompt = ExtractedPrompt(
                    content=text,
                    byte_offset=offset,
                    length=len(text),
                    word_count=word_count,
                    category=classify_prompt(text),
                    file_references=extract_file_references(text),
                    has_code_block=has_code_block(text),
                    imperative_verbs=extract_imperative_verbs(text),
                    source_file=source_file or pb_path.stem
                )
                prompts.append(prompt)

    return prompts


def list_conversations(conversations_path: Path) -> list[tuple[str, int, datetime]]:
    """List all conversation files with metadata."""
    conversations = []

    for pb_file in conversations_path.glob("*.pb"):
        conv_id = pb_file.stem
        size = pb_file.stat().st_size
        mtime = datetime.fromtimestamp(pb_file.stat().st_mtime)
        conversations.append((conv_id, size, mtime))

    conversations.sort(key=lambda x: x[2], reverse=True)
    return conversations


# ============================================================================
# Statistics Functions
# ============================================================================

def calculate_stats(prompts: list[ExtractedPrompt]) -> PromptStats:
    """Calculate statistics from extracted prompts."""
    if not prompts:
        return PromptStats()

    total_words = sum(p.word_count for p in prompts)
    avg_words = total_words / len(prompts) if prompts else 0

    category_counts = Counter(p.category for p in prompts)

    all_verbs = []
    for p in prompts:
        all_verbs.extend(p.imperative_verbs)
    common_verbs = Counter(all_verbs).most_common(15)

    word_count_dist = {
        "1-5 words": 0,
        "6-15 words": 0,
        "16-30 words": 0,
        "31-50 words": 0,
        "51-100 words": 0,
        "100+ words": 0,
    }
    for p in prompts:
        if p.word_count <= 5:
            word_count_dist["1-5 words"] += 1
        elif p.word_count <= 15:
            word_count_dist["6-15 words"] += 1
        elif p.word_count <= 30:
            word_count_dist["16-30 words"] += 1
        elif p.word_count <= 50:
            word_count_dist["31-50 words"] += 1
        elif p.word_count <= 100:
            word_count_dist["51-100 words"] += 1
        else:
            word_count_dist["100+ words"] += 1

    start_patterns = []
    for p in prompts:
        words = p.content.lower().split()[:3]
        if len(words) >= 2:
            start_patterns.append(' '.join(words[:2]))
    common_patterns = Counter(start_patterns).most_common(10)

    source_files = set(p.source_file for p in prompts if p.source_file)

    return PromptStats(
        total_prompts=len(prompts),
        total_words=total_words,
        avg_words=round(avg_words, 1),
        category_counts=dict(category_counts),
        common_verbs=common_verbs,
        common_patterns=common_patterns,
        word_count_distribution=word_count_dist,
        files_processed=len(source_files) if source_files else 1
    )


# ============================================================================
# Output Formatting
# ============================================================================

def format_stats_markdown(stats: PromptStats) -> str:
    """Format statistics as markdown."""
    lines = [
        "# Prompt Analysis Statistics",
        "",
        f"**Total prompts:** {stats.total_prompts}",
        f"**Total words:** {stats.total_words:,}",
        f"**Average words/prompt:** {stats.avg_words}",
        f"**Conversations processed:** {stats.files_processed}",
        "",
        "## Category Distribution",
        "",
        "| Category | Count | % |",
        "|----------|-------|---|",
    ]

    for cat, count in sorted(stats.category_counts.items(), key=lambda x: -x[1]):
        pct = 100 * count / stats.total_prompts if stats.total_prompts else 0
        lines.append(f"| {cat} | {count} | {pct:.1f}% |")

    lines.extend([
        "",
        "## Word Count Distribution",
        "",
        "| Range | Count | % |",
        "|-------|-------|---|",
    ])

    for range_name, count in stats.word_count_distribution.items():
        pct = 100 * count / stats.total_prompts if stats.total_prompts else 0
        lines.append(f"| {range_name} | {count} | {pct:.1f}% |")

    if stats.common_verbs:
        lines.extend([
            "",
            "## Most Common Action Verbs",
            "",
            "| Verb | Count |",
            "|------|-------|",
        ])
        for verb, count in stats.common_verbs:
            lines.append(f"| {verb} | {count} |")

    if stats.common_patterns:
        lines.extend([
            "",
            "## Common Starting Patterns",
            "",
            "| Pattern | Count |",
            "|---------|-------|",
        ])
        for pattern, count in stats.common_patterns:
            lines.append(f"| {pattern} | {count} |")

    return '\n'.join(lines)


def format_prompts_markdown(
    prompts: list[ExtractedPrompt],
    conversation_id: str = None,
    include_analysis: bool = False,
    stats: PromptStats = None
) -> str:
    """Format extracted prompts as markdown."""
    lines = ["# Extracted User Prompts", ""]

    if conversation_id:
        lines.extend([f"**Conversation:** `{conversation_id}`", ""])

    lines.append(f"**Total prompts:** {len(prompts)}")

    if stats:
        lines.append(f"**Average prompt length:** {stats.avg_words} words")

    lines.extend(["", "---", ""])

    for i, prompt in enumerate(prompts, 1):
        meta = f"({prompt.word_count} words"
        if include_analysis:
            meta += f", {prompt.category}"
            if prompt.file_references:
                meta += f", {len(prompt.file_references)} file refs"
        meta += ")"

        lines.extend([
            f"## Prompt {i} {meta}",
            "",
        ])

        if include_analysis and prompt.imperative_verbs:
            lines.append(f"**Verbs:** {', '.join(prompt.imperative_verbs)}")
            lines.append("")

        lines.extend([
            prompt.content,
            "",
            "---",
            ""
        ])

    return '\n'.join(lines)


def format_training_output(prompts: list[ExtractedPrompt]) -> str:
    """Format prompts for training/review purposes."""
    lines = [
        "# Prompt Training Review",
        "",
        "Use this document to review your prompting patterns and identify areas for improvement.",
        "",
        "## Quick Tips",
        "",
        "- **Be specific**: Include exact file names, function names, expected behavior",
        "- **Provide context**: Reference related files with @[file] syntax",
        "- **Clear intent**: Start with action verb (create, fix, update, explain)",
        "- **One request**: Focus on a single task per prompt when possible",
        "",
        "---",
        "",
    ]

    by_category = {}
    for p in prompts:
        by_category.setdefault(p.category, []).append(p)

    for category in [PromptCategory.COMMAND, PromptCategory.QUESTION,
                     PromptCategory.CONTEXT, PromptCategory.CORRECTION,
                     PromptCategory.FEEDBACK, PromptCategory.OTHER]:
        if category in by_category:
            lines.extend([
                f"## {category.title()} Prompts ({len(by_category[category])})",
                "",
            ])

            for i, p in enumerate(by_category[category], 1):
                quality = "✅" if p.word_count >= 10 and p.imperative_verbs else "⚠️"
                lines.extend([
                    f"### {quality} Example {i} ({p.word_count} words)",
                    "",
                    f"```",
                    p.content,
                    f"```",
                    "",
                ])

                if p.word_count < 10 and not p.file_references:
                    lines.extend([
                        "> 💡 **Tip:** This prompt is short. Consider adding:",
                        "> - Specific file references",
                        "> - Expected outcome",
                        "> - Context from related work",
                        "",
                    ])

            lines.append("")

    return '\n'.join(lines)


def format_json_output(
    prompts: list[ExtractedPrompt],
    stats: PromptStats = None
) -> str:
    """Format output as JSON."""
    data = {
        'prompts': [
            {
                'content': p.content,
                'word_count': p.word_count,
                'category': p.category,
                'file_references': p.file_references,
                'has_code_block': p.has_code_block,
                'imperative_verbs': p.imperative_verbs,
                'source_file': p.source_file,
            }
            for p in prompts
        ],
    }
    if stats:
        data['statistics'] = {
            'total_prompts': stats.total_prompts,
            'total_words': stats.total_words,
            'avg_words': stats.avg_words,
            'category_counts': stats.category_counts,
            'common_verbs': stats.common_verbs,
            'word_count_distribution': stats.word_count_distribution,
            'files_processed': stats.files_processed,
        }
    return json.dumps(data, indent=2, ensure_ascii=False)


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Extract and analyze user prompts from Antigravity conversation files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list                        # List all conversations
  %(prog)s                               # Extract from most recent conversation
  %(prog)s ca7d88fe-1b9e-48a3            # Extract from specific (partial ID match)
  %(prog)s --all --analyze               # All conversations with categorization
  %(prog)s --stats                       # Statistics only
  %(prog)s --training                    # Training-focused format
  %(prog)s --all --json --analyze        # Full JSON output
        """
    )

    parser.add_argument(
        'conversation_id',
        nargs='?',
        help='Conversation ID (or partial ID) to extract from'
    )

    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List all available conversations'
    )

    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Extract from all conversations'
    )

    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output file path (default: stdout)'
    )

    parser.add_argument(
        '--json', '-j',
        action='store_true',
        help='Output as JSON'
    )

    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Include prompt categorization and analysis'
    )

    parser.add_argument(
        '--stats', '-s',
        action='store_true',
        help='Output statistics only (no prompts)'
    )

    parser.add_argument(
        '--training', '-t',
        action='store_true',
        help='Format output for training/review'
    )

    parser.add_argument(
        '--path', '-p',
        type=Path,
        default=DEFAULT_CONVERSATIONS_PATH,
        help=f'Path to conversations folder (default: {DEFAULT_CONVERSATIONS_PATH})'
    )

    parser.add_argument(
        '--include-trivial',
        action='store_true',
        help='Include trivial responses like "continue", "yes"'
    )

    parser.add_argument(
        '--limit', '-n',
        type=int,
        default=10,
        help='Limit number of conversations to process with --all (default: 10)'
    )

    args = parser.parse_args()

    # Validate path
    if not args.path.exists():
        print(f"Error: Conversations path not found: {args.path}", file=sys.stderr)
        sys.exit(1)

    conversations = list_conversations(args.path)

    if args.list:
        print(f"# Antigravity Conversations ({len(conversations)} total)\n")
        print(f"{'ID':<40} {'Size':>12} {'Modified':<20}")
        print("-" * 75)
        for conv_id, size, mtime in conversations:
            size_str = f"{size / 1024:.1f} KB" if size < 1024*1024 else f"{size / (1024*1024):.1f} MB"
            print(f"{conv_id:<40} {size_str:>12} {mtime.strftime('%Y-%m-%d %H:%M'):<20}")
        return

    # Determine which conversations to process
    target_conversations = []

    if args.all:
        target_conversations = [c[0] for c in conversations[:args.limit]]
    elif args.conversation_id:
        matches = [c[0] for c in conversations if args.conversation_id.lower() in c[0].lower()]
        if not matches:
            print(f"Error: No conversation matching '{args.conversation_id}'", file=sys.stderr)
            sys.exit(1)
        target_conversations = matches[:1]
    else:
        if conversations:
            target_conversations = [conversations[0][0]]
        else:
            print("Error: No conversations found", file=sys.stderr)
            sys.exit(1)

    # Extract prompts
    all_prompts = []

    for conv_id in target_conversations:
        pb_path = args.path / f"{conv_id}.pb"
        print(f"Processing: {conv_id}...", file=sys.stderr)

        try:
            prompts = extract_prompts_from_pb(
                pb_path,
                include_trivial=args.include_trivial,
                source_file=conv_id
            )
            all_prompts.extend(prompts)
            print(f"  Found {len(prompts)} prompts", file=sys.stderr)
        except Exception as e:
            print(f"  Error: {e}", file=sys.stderr)

    # Calculate stats
    stats = calculate_stats(all_prompts)

    # Format output
    if args.stats:
        output = format_stats_markdown(stats)
    elif args.training:
        output = format_training_output(all_prompts)
    elif args.json:
        output = format_json_output(all_prompts, stats if args.analyze else None)
    else:
        conv_label = target_conversations[0] if len(target_conversations) == 1 else f"{len(target_conversations)} conversations"
        output = format_prompts_markdown(
            all_prompts,
            conversation_id=conv_label,
            include_analysis=args.analyze,
            stats=stats if args.analyze else None
        )

    # Write output
    if args.output:
        args.output.write_text(output, encoding='utf-8')
        print(f"\nExtracted {len(all_prompts)} prompts to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()
