import yaml
from functions import load_prompts, get_last_replies, generate_response_chat, post_comment_to_existing_submission
import praw
import openai
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config

def process_title(reddit, subreddit_name, prompt_text, num_posts, title, idx):
    try:
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
            return
        body = response_text

        # Post to subreddit
        submission = post_comment_to_existing_submission(reddit, subreddit_name, title, body)
        if submission:
            print(f"{idx}: Posted to {subreddit_name}: {title}")
        else:
            print(f"Failed to post to {subreddit_name}.")

    except Exception as e:
        print(f"Error processing title {title} in subreddit {subreddit_name}: {e}")

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
        subreddit_name = prompt_data.get('subreddits')
        prompt_text = prompt_data.get('prompt')
        num_posts = prompt_data.get('num_posts')
        titles = prompt_data.get('titles')

        num_new_comments = 2

        # Loop over num_new_comments sequentially
        for idx in range(num_new_comments):
            # Use ThreadPoolExecutor with 6 threads for processing titles concurrently
            with ThreadPoolExecutor(max_workers=6) as executor:
                # Submit each title as a separate task
                futures = [
                    executor.submit(process_title, reddit, subreddit_name, prompt_text, num_posts, title, idx)
                    for title in titles
                ]

                # Wait for all tasks to complete
                for future in as_completed(futures):
                    try:
                        future.result()  # This will raise any exception that occurred in the thread
                    except Exception as e:
                        print(f"Error in threaded execution for titles: {e}")

if __name__ == '__main__':
    main()