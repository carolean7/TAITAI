# main.py

import yaml
from functions import load_prompts, get_last_posts, generate_response_chat, post_to_subreddit
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
        num_posts = prompt_data.get('num_posts', 5)
        title_template = prompt_data.get('title', 'Generated Post')

        for subreddit_name in subreddits:
            try:
                # Get last X posts
                # last_posts = get_last_posts(reddit, subreddit_name, num_posts)

                # Replace {placeholder} in prompt_text
                # full_prompt = prompt_text.replace('{placeholder}', last_posts)

                # Prepare messages for ChatCompletion
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "full_prompt"}
                ]

                # Generate response
                response_text = generate_response_chat(messages)
                print(response_text)
                if not response_text:
                    print(f"Failed to generate response for subreddit {subreddit_name}.")
                    continue

                # Prepare title and body
                title = title_template
                body = response_text

                # Post to subreddit
                submission = post_to_subreddit(reddit, subreddit_name, title, body)
                if submission:
                    print(f"Posted to {subreddit_name}: {submission.title} (URL: {submission.url})")
                else:
                    print(f"Failed to post to {subreddit_name}.")

            except Exception as e:
                print(f"Error processing subreddit {subreddit_name}: {e}")

if __name__ == '__main__':
    main()