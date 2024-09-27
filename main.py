# main.py

import yaml
from functions import load_prompts, get_last_replies, generate_response_chat, post_comment_to_existing_submission
import praw
import openai
import os

def load_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config

def main():
    # Load configurations
    config = load_config('config.yaml')

    # Initialize Reddit instance
    reddit = praw.Reddit(
        client_id=config['reddit']['client_id'],
        client_secret=config['reddit']['client_secret'],
        username=config['reddit']['username'],
        password=config['reddit']['password'],
        user_agent=config['reddit']['user_agent']
    )

    # Set OpenAI API key
    openai.api_key = config['openai']['api_key']

    # Load prompts
    prompts = load_prompts('prompts')

    # For each prompt, process
    for prompt_data in prompts:
        # Get variables from prompt_data
        subreddits = prompt_data.get('subreddits', [])
        prompt_text = prompt_data.get('prompt', '')
        num_posts = prompt_data.get('num_posts', 1)
        title_template = prompt_data.get('title', 'Generated Post')

        for subreddit_name in subreddits:
            try:
                title = title_template

                # Get last posts
                last_posts = get_last_replies(reddit, subreddit_name, title, num_posts)

                # Replace {placeholder} in prompt_text
                full_prompt = prompt_text.replace('{placeholder}', last_posts)

                # Prepare messages for ChatCompletion
                messages = [
                    {"role": "system", "content": "You are a respected Reddit Poster."},
                    {"role": "user", "content": full_prompt}
                ]

                # Generate response
                response_text = generate_response_chat(messages)
                if not response_text:
                    print(f"Failed to generate response for subreddit {subreddit_name}.")
                    continue
                body = response_text


                # Post to subreddit
                submission = post_comment_to_existing_submission(reddit, subreddit_name, title, body)
                if submission:
                    print(f"Posted to {subreddit_name}: {title}")
                else:
                    print(f"Failed to post to {subreddit_name}.")

            except Exception as e:
                print(f"Error processing subreddit {subreddit_name}: {e}")

if __name__ == '__main__':
    for i in range(2):
        main()