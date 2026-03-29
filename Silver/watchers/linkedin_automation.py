"""
LinkedIn Automation System
Generates business content and posts automatically to LinkedIn
"""
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict


class LinkedInAutomation:
    """Handles LinkedIn content generation and posting"""

    def __init__(self, vault_path: str, config_path: str = './linkedin_config.json'):
        self.vault_path = Path(vault_path)
        self.config_path = Path(config_path)
        self.posts_dir = self.vault_path / 'LinkedIn_Posts'
        self.posts_dir.mkdir(parents=True, exist_ok=True)

        self.scheduled_dir = self.posts_dir / 'Scheduled'
        self.published_dir = self.posts_dir / 'Published'
        self.drafts_dir = self.posts_dir / 'Drafts'

        for dir in [self.scheduled_dir, self.published_dir, self.drafts_dir]:
            dir.mkdir(parents=True, exist_ok=True)

        self.config = self._load_config()
        self.post_templates = self._load_templates()

    def _load_config(self) -> dict:
        """Load LinkedIn configuration"""
        default_config = {
            "posting_schedule": {
                "days": ["Tuesday", "Wednesday", "Thursday"],
                "times": ["09:00", "11:00"]
            },
            "content_topics": [
                "AI automation",
                "Business efficiency",
                "Tech trends",
                "Productivity tips",
                "Case studies"
            ],
            "hashtags": [
                "#AI",
                "#Automation",
                "#BusinessGrowth",
                "#Productivity",
                "#TechInnovation"
            ],
            "target_audience": "Business owners and tech professionals",
            "tone": "Professional yet approachable"
        }

        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config

    def _load_templates(self) -> List[Dict]:
        """Load post templates for content generation"""
        return [
            {
                "type": "insight",
                "template": """🚀 {insight_title}

{main_content}

Key takeaways:
• {takeaway_1}
• {takeaway_2}
• {takeaway_3}

What's your experience with this? Share in the comments!

{hashtags}"""
            },
            {
                "type": "case_study",
                "template": """📊 Case Study: {case_title}

Challenge: {challenge}

Solution: {solution}

Results: {results}

Want to achieve similar results? Let's connect!

{hashtags}"""
            },
            {
                "type": "tip",
                "template": """💡 Pro Tip: {tip_title}

{tip_content}

Try this today and let me know how it works for you!

{hashtags}"""
            },
            {
                "type": "question",
                "template": """🤔 Question for my network:

{question}

{context}

Drop your thoughts in the comments! 👇

{hashtags}"""
            }
        ]

    def generate_post_content(self, topic: str, post_type: str = "insight") -> str:
        """
        Generate LinkedIn post content

        In production, this would use Claude API to generate content.
        For this hackathon, we'll create structured templates.

        Args:
            topic: The topic to write about
            post_type: Type of post (insight, case_study, tip, question)

        Returns:
            Generated post content
        """
        template = next((t for t in self.post_templates if t['type'] == post_type), self.post_templates[0])

        # Sample content generation (in production, use Claude API)
        content_map = {
            "insight": {
                "insight_title": f"The Future of {topic}",
                "main_content": f"After working with dozens of businesses, I've noticed a clear trend: {topic} is transforming how we work. Companies that embrace this early are seeing 3x productivity gains.",
                "takeaway_1": "Start small with pilot projects",
                "takeaway_2": "Measure everything and iterate",
                "takeaway_3": "Focus on ROI, not just features",
                "hashtags": " ".join(self.config['hashtags'][:5])
            },
            "tip": {
                "tip_title": f"Boost Your {topic} Strategy",
                "tip_content": f"Here's a simple framework I use:\n\n1. Identify repetitive tasks\n2. Automate the low-hanging fruit\n3. Measure time saved\n4. Reinvest in high-value work\n\nThis approach has saved my clients 20+ hours per week.",
                "hashtags": " ".join(self.config['hashtags'][:5])
            },
            "question": {
                "question": f"How are you leveraging {topic} in your business?",
                "context": f"I'm curious to hear different perspectives on {topic}. Some swear by full automation, others prefer a hybrid approach.",
                "hashtags": " ".join(self.config['hashtags'][:5])
            }
        }

        data = content_map.get(post_type, content_map["insight"])
        return template['template'].format(**data)

    def create_scheduled_post(self, content: str, scheduled_time: datetime) -> Path:
        """
        Create a scheduled post file

        Args:
            content: Post content
            scheduled_time: When to publish

        Returns:
            Path to scheduled post file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'POST_{timestamp}.md'
        filepath = self.scheduled_dir / filename

        post_data = f"""---
type: linkedin_post
created: {datetime.now().isoformat()}
scheduled_for: {scheduled_time.isoformat()}
status: scheduled
approval_required: false
---

# LinkedIn Post - Scheduled

## Scheduled Time
{scheduled_time.strftime('%Y-%m-%d %H:%M')}

## Content
{content}

## Actions
- [ ] Review content
- [ ] Approve for posting
- [ ] Track engagement after posting

---
*Generated by LinkedIn Automation at {datetime.now().isoformat()}*
"""

        filepath.write_text(post_data, encoding='utf-8')
        return filepath

    def generate_weekly_content(self) -> List[Path]:
        """
        Generate a week's worth of LinkedIn posts

        Returns:
            List of created post files
        """
        posts = []
        topics = self.config['content_topics']
        post_types = ['insight', 'tip', 'question']

        # Generate 5 posts for the week
        for i in range(5):
            topic = topics[i % len(topics)]
            post_type = post_types[i % len(post_types)]

            content = self.generate_post_content(topic, post_type)

            # Schedule for next available slot
            scheduled_time = self._get_next_posting_slot(i)

            filepath = self.create_scheduled_post(content, scheduled_time)
            posts.append(filepath)

        return posts

    def _get_next_posting_slot(self, offset: int = 0) -> datetime:
        """Get the next available posting time based on schedule"""
        schedule = self.config['posting_schedule']
        days_map = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2,
            'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }

        now = datetime.now()
        target_days = [days_map[d] for d in schedule['days']]

        # Find next scheduled day
        days_ahead = 0
        slots_checked = 0

        while slots_checked <= offset:
            check_date = now + timedelta(days=days_ahead)
            if check_date.weekday() in target_days:
                slots_checked += 1
                if slots_checked > offset:
                    # Use first time slot
                    time_str = schedule['times'][0]
                    hour, minute = map(int, time_str.split(':'))
                    return check_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            days_ahead += 1

        return now + timedelta(days=1)

    def get_pending_posts(self) -> List[Path]:
        """Get all scheduled posts ready to publish"""
        now = datetime.now()
        pending = []

        for post_file in self.scheduled_dir.glob('*.md'):
            content = post_file.read_text(encoding='utf-8')

            # Extract scheduled time from frontmatter
            if 'scheduled_for:' in content:
                for line in content.split('\n'):
                    if 'scheduled_for:' in line:
                        time_str = line.split('scheduled_for:')[1].strip()
                        scheduled_time = datetime.fromisoformat(time_str)

                        if scheduled_time <= now:
                            pending.append(post_file)
                        break

        return pending

    def publish_post(self, post_file: Path) -> bool:
        """
        Publish a post to LinkedIn

        In production, this would use LinkedIn API or browser automation.
        For this hackathon, we'll move it to Pending_Approval for human review.

        Args:
            post_file: Path to the post file

        Returns:
            True if successful
        """
        try:
            # Move to Pending_Approval for human review
            approval_dir = self.vault_path / 'Pending_Approval'
            approval_dir.mkdir(parents=True, exist_ok=True)

            new_path = approval_dir / post_file.name

            # Update content to indicate it needs approval
            content = post_file.read_text(encoding='utf-8')
            content = content.replace('status: scheduled', 'status: pending_approval')
            content += f"\n\n## Approval Required\nMove this file to /Approved to publish, or /Rejected to cancel.\n"

            new_path.write_text(content, encoding='utf-8')
            post_file.unlink()  # Remove from scheduled

            return True

        except Exception as e:
            print(f"Error publishing post: {e}")
            return False


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent / 'vault'

    automation = LinkedInAutomation(str(vault_path))

    # Generate weekly content
    print("Generating weekly LinkedIn content...")
    posts = automation.generate_weekly_content()
    print(f"Created {len(posts)} scheduled posts")

    # Check for pending posts
    pending = automation.get_pending_posts()
    if pending:
        print(f"\nFound {len(pending)} posts ready to publish")
        for post in pending:
            automation.publish_post(post)
            print(f"Moved {post.name} to Pending_Approval")
