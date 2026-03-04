#!/usr/bin/env python
"""CLI tool for testing LLM-based feedback intelligence."""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.sentiment import analyze_feedback_advanced, analyze_feedback_batch


def test_single_feedback(feedback: str, provider: str = "local"):
    """Test analysis of single feedback item."""
    print(f"\n📝 Feedback: {feedback}\n")
    print(f"🤖 Provider: {provider}")
    print(f"🔄 Analyzing...\n")

    try:
        result = analyze_feedback_advanced(feedback, provider=provider)

        print(f"✅ Sentiment: {result.get('sentiment').upper()}")
        print(f"📊 Confidence: {result.get('confidence', 0):.0%}")

        print("\n🎯 Aspects Detected:")
        aspects = result.get("aspects", {})
        if aspects:
            for aspect, details in aspects.items():
                print(f"  • {aspect.replace('_', ' ').title()}: {details.get('score')}")
                print(f"    Evidence: {details.get('evidence', 'N/A')}")
        else:
            print("  (None)")

        print("\n🏷️ Auto-Tags:")
        tags = result.get("tags", [])
        if tags:
            for tag in tags:
                print(f"  • {tag.replace('_', ' ').title()}")
        else:
            print("  (None)")

        print("\n🔍 Root Causes:")
        causes = result.get("root_causes", [])
        if causes:
            for cause in causes:
                print(f"  • {cause.replace('_', ' ').title()}")
        else:
            print("  (None)")

        print("\n💡 Recommendations:")
        recommendations = result.get("recommendations", [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print("  (None)")

        print(f"\n📄 Summary: {result.get('summary', 'N/A')}")

        return result

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def test_batch_analysis(feedback_list: list, provider: str = "local"):
    """Test batch analysis with aggregation."""
    print(f"\n📊 Batch Analysis ({len(feedback_list)} items)")
    print(f"🤖 Provider: {provider}")
    print(f"🔄 Analyzing...\n")

    try:
        result = analyze_feedback_batch(feedback_list, provider=provider)

        print(f"✅ Total Analyzed: {result.get('total_feedback', 0)}")

        print("\n📈 Sentiment Distribution:")
        dist = result.get("sentiment_distribution", {})
        for sentiment, count in dist.items():
            pct = (count / result.get("total_feedback", 1)) * 100
            print(f"  • {sentiment.replace('_', ' ').title()}: {count} ({pct:.0f}%)")

        print("\n🚨 Top Issues:")
        issues = result.get("top_issues", [])
        if issues:
            for issue in issues:
                print(f"  • {issue.replace('_', ' ').title()}")
        else:
            print("  (None)")

        print("\n✨ Priority Improvements:")
        improvements = result.get("priority_improvements", [])
        if improvements:
            for imp in improvements:
                print(f"  • {imp.replace('_', ' ').title()}")
        else:
            print("  (None)")

        return result

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def interactive_mode(provider: str = "local"):
    """Interactive testing mode."""
    print(f"\n🎯 LLM Feedback Intelligence - Interactive Mode")
    print(f"Provider: {provider}")
    print("Type 'exit' to quit, 'batch' for batch mode, 'help' for help\n")

    while True:
        feedback = input("📝 Enter feedback (or command): ").strip()

        if feedback.lower() == "exit":
            print("\n👋 Goodbye!")
            break
        elif feedback.lower() == "help":
            print("""
Commands:
  exit              - Exit interactive mode
  batch             - Switch to batch analysis
  help              - Show this help
  
Examples:
  "Great service!" - Analyze single feedback
  "The waiter was slow but friendly" - Complex feedback
            """)
        elif feedback.lower() == "batch":
            print("\n🔄 Batch Mode:")
            feedback_text = input("Enter feedback items (one per line, empty line to finish):\n")
            items = [f.strip() for f in feedback_text.split("\n") if f.strip()]
            if items:
                test_batch_analysis(items, provider)
        elif feedback:
            test_single_feedback(feedback, provider)


def main():
    parser = argparse.ArgumentParser(
        description="Test LLM-based feedback intelligence"
    )
    parser.add_argument(
        "feedback",
        nargs="?",
        help="Feedback text to analyze (if empty, interactive mode)",
    )
    parser.add_argument(
        "--provider",
        choices=["local", "openai", "gemini"],
        default="local",
        help="Sentiment analysis provider",
    )
    parser.add_argument(
        "--batch",
        nargs="+",
        help="Batch analyze multiple feedback items",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Interactive mode",
    )
    parser.add_argument(
        "--examples",
        "-e",
        action="store_true",
        help="Show example outputs",
    )

    args = parser.parse_args()

    if args.examples:
        print("""
🎯 LLM Feedback Intelligence - Examples

Example 1: Basic Positive Feedback
  Feedback: "Great service!"
  Sentiment: positive
  Tags: [good_service]
  Aspects: service_speed (positive), staff_behavior (positive)

Example 2: Mixed Feedback
  Feedback: "Good food but slow service"
  Sentiment: positive (food dominates)
  Tags: [excellent_food, slow_service]
  Root Causes: [understaffed]
  Recommendations: [Increase staff during peak hours]

Example 3: Negative Feedback
  Feedback: "Rude waiter and cold food"
  Sentiment: negative
  Tags: [rude_staff, poor_food_quality]
  Root Causes: [staff_training_gap, kitchen_issues]
  Recommendations: [Conduct customer service training, Review kitchen processes]

Example 4: Detailed Feedback
  Feedback: "The table was dirty, staff was inattentive, but food was amazing"
  Sentiment: neutral (mixed signals)
  Aspects:
    - cleanliness: negative (dirty table)
    - staff_behavior: negative (inattentive)
    - food_quality: positive (amazing)
  Tags: [hygiene_issue, inattentive_staff, excellent_food]
  Root Causes: [maintenance_gap, understaffed]
        """)
        return

    if args.interactive:
        interactive_mode(args.provider)
    elif args.batch:
        result = test_batch_analysis(args.batch, args.provider)
        if args.json:
            print(json.dumps(result, indent=2))
    elif args.feedback:
        result = test_single_feedback(args.feedback, args.provider)
        if args.json:
            print(json.dumps(result, indent=2))
    else:
        interactive_mode(args.provider)


if __name__ == "__main__":
    main()
