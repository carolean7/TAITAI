# functions.py

import yaml
import os
import praw
import openai

def load_prompts(prompts_dir):
    """
    Load all YAML prompt files from the prompts directory.
    """
    prompts = []
    for filename in os.listdir(prompts_dir):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            with open(os.path.join(prompts_dir, filename), 'r') as f:
                prompt_data = yaml.safe_load(f)
                prompts.append(prompt_data)
    return prompts

def get_last_posts(reddit_instance, subreddit_name, num_posts):
    """
    Get the last num_posts from subreddit_name.
    """
    subreddit = reddit_instance.subreddit(subreddit_name)
    posts = []
    for submission in subreddit.new(limit=num_posts):
        # Combine the title and selftext
        post_content = f"Title: {submission.title}\n\n{submission.selftext}"
        posts.append(post_content)
    return '\n\n---\n\n'.join(posts)

def generate_response_chat(messages):
    """
    Generate a response using OpenAI's ChatCompletion API.
    """
    try:
        response = openai.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            max_tokens=10000,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

def post_to_subreddit(reddit_instance, subreddit_name, title, body):
    """
    Post to a subreddit with the given title and body.
    """
    try:
        subreddit = reddit_instance.subreddit(subreddit_name)
        submission = subreddit.submit(title, selftext=body)
        return submission
    except Exception as e:
        print(f"Reddit API error when posting to {subreddit_name}: {e}")
        return None