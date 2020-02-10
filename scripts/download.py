#!/usr/bin/env python3

# On Using Twitter's Internal API 
# 
# Per experiments with cURL, using Twitter's private API 
# requires, at least, an 'authorization' token (some endpoints
# require a minimum amount of url parameters). If you review 
# the request logs made by Twitter's website, you'll see that
# each API request is accompanied by a magical 'authorization'
# header seemingly generated out of thin air. Usually to source
# a bearer token, per [1], you make a request to the /oauth2/token
# endpoint. In the case of the frontend, no such request is ever 
# made. Where then does it come from? 
# 
# After some RE, it seems that Twitter embeds said token in it's
# JS bundles. If you search through the 'main' bundle for the 
# bearer token observed in API requests, you'll find that it's 
# stored as a static variable. In mine, it's assigned to a variable
# 's' and is retrieved through, I assume, a obfuscated getter method
# defined on a class. 
#
# On it's own this isn't that novel, but what's useful is that if you
# make a request for the JS bundle from your terminal, that is without
# context available to identify you as a user, you'll notice that the
# token is unchanged. 
#
# So, it's probably the case that either:  Twitter generates an authorization
# token per IP, or, Twitter uses a 'backdoor' token across all devices for
# frontend use.
#
# It's unclear as of yet whether this token is rotated or deprectiated.
#
# [1] Using Bearer Tokens, https://developer.twitter.com/en/docs/basics/authentication/guides/bearer-tokens

import requests
import json
import os

class Twitter:
    version = '1.1'
    url = 'https://api.twitter.com'

    def __init__(self, username, bearer_token):
        self.username = username
        self.headers = {
            'authorization': 'Bearer {}'.format(bearer_token)
        }

    def follows(self, count=200, verbose=False):
        users = []
        cursor = '-1'
        route = "/{}/friends/list.json".format(self.version) 


        while cursor != '0': 
            if verbose:
                print('User count: {}'.format(len(users)))


            params = "?screen_name={}&cursor={}&count={}".format(
                self.username, cursor, count
            )

            response = requests.get(
                self.url+route+params, 
                headers=self.headers
            ).json()

            users = response.get('users', []) + users

            cursor = response['next_cursor_str']

        return users

if __name__ == '__main__':
    import pandas as pd
    import numpy as np

    if 'TWITTER_BEARER_TOKEN' not in os.environ:
       raise Exception('TWITTER_BEARER_TOKEN must be set.')

    token = os.environ['TWITTER_BEARER_TOKEN']

    accounts = {
        'computer-science': 'compsci_twitr',
        'economics': 'economics_twitr',
        'statistics': 'stats_twitr',
        'mathematics': 'math_twitr'
    }

    for domain, username in accounts.items():
        path = '{}.csv'.format(domain)

        print('Downloading followers.')
        account = Twitter(username, token)
        follows = account.follows(verbose=True)

        print('Quick house keeping.')
        users = pd.DataFrame(follows)
        height, width = users.shape

        # Tease out missing values
        users[users == 'none'] = np.nan

        # Remove empty columns
        nonempty_columns = users.columns[users.isna().sum() != height]
        users = users[nonempty_columns]
    
        # Remove useless columns
        users = users.drop(
            columns=[
                'status',
                'pinned_tweet_ids',
                'pinned_tweet_ids_str',
                'advertiser_account_service_levels',
                'entities',
            ]        
        )

        print('Saving to {}'.format(path))
        users.to_csv(path, index=False)
