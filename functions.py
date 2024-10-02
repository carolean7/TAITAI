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

def get_last_replies(reddit_instance, subreddit_name, post_title, num_replies):
    """
    Get the original post and the last num_replies from the Reddit post with the title 'post_title'
    in the subreddit 'subreddit_name'.
    """
    try:
        # Search for the post by title in the subreddit
        subreddit = reddit_instance.subreddit(subreddit_name)
        search_results = subreddit.search(post_title, sort='new', time_filter='all')

        # Find the post with the exact title
        for submission in search_results:
            if submission.title == post_title:
                # Fetch the post content (title and selftext)
                post_content = f"Title: {submission.title}\n\n{submission.selftext}"

                # Fetch the comments from the submission
                submission.comments.replace_more(limit=0)  # Load all comments
                comments = submission.comments.list()

                # Get the most recent comments (sorted by the newest)
                recent_comments = sorted(comments, key=lambda c: c.created_utc, reverse=True)[:num_replies]
                
                # Combine the comment bodies into a single string
                comment_bodies = [f"{comment.body}" for comment in recent_comments]

                # Combine the original post content with the comments
                return post_content + "\n\n---\n\n" + '\n\n---\n\n'.join(comment_bodies)

        # If post with title is not found
        return f"Post with title '{post_title}' not found in subreddit '{subreddit_name}'."

    except Exception as e:
        print(f"Reddit API error: {e}")
        return None

def generate_response_chat(messages):
    """
    Generate a response using OpenAI's ChatCompletion API.
    """
    try:
        response = openai.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            max_tokens=3000,
            n=1,
            stop=None,
            temperature=1,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

def post_comment_to_existing_submission(reddit_instance, subreddit_name, post_title, body):
    """
    Post a comment to an existing Reddit post identified by its title.
    """
    try:
        # Get the subreddit object
        subreddit = reddit_instance.subreddit(subreddit_name)
        
        # Search for the existing post by title
        search_results = subreddit.search(post_title, sort='new', time_filter='all')
        
        # Iterate through the search results to find the post with the exact title
        for submission in search_results:
            if isinstance(submission, praw.models.Submission) and submission.title == post_title:
                # Post a comment on the existing submission
                comment = submission.reply(body)
                return comment

        print(f"Post with title '{post_title}' not found in subreddit '{subreddit_name}'.")
        return None
    
    except Exception as e:
        print(f"Reddit API error when replying to post in {subreddit_name}: {e}")
        return None