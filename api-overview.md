# API Overview

- [Current Version](#current-version)
- [Authentication](#authentication)
- [Authorization](#authorization)
- [Schema](#schema)
- [Pagination](#pagination)
- [API Endpoints](#api-endpoints)
- [Errors](#errors)


## Current Version

The CoinsWallet API is currently at version 1.0, use the following base URI to access version 1.0 endpoints.

    http://localhost:8000/api/v1/

## Authentication

The CoinsWallet API follows OAuth 2 for authentication, require requests to include the `access_token` to authenticate the client. 
Use `grant_type=password` to authenticate with `username` and `password`, along with application's `client_id` and `client_secret`.
    
> Auth URL: http://localhost:8000/o/token/

> Response contains: `access_token`, `token_type`, `expires_in`, `refresh_token` and `scope` parameters.

> __Scope consists__
    transact: Transaction rights
    view : View rights

    Example:
    username = `kaushal`
    password = `secret_pass`
    client_id = `6LnALs4wMmYcVPn7Tol6joXpJXSEb9BCEsr3o6Bn`
    client_secret = `uzDYdXGbbYBstWmo06YmNuLG2IxBviUMpT3pFYaMcptPYaMMAnWYSI86Ngx6BWCi5UlVQHcUYjP0HPbDONGycD6fYJN75TAYfDeWptFcYM8zDdpZTaXfwg4s9KXJBKJl`
    
    $ curl -X POST -d "grant_type=password&username=kaushal&password=secret_pass" -u"6LnALs4wMmYcVPn7Tol6joXpJXSEb9BCEsr3o6Bn:uzDYdXGbbYBstWmo06YmNuLG2IxBviUMpT3pFYaMcptPYaMMAnWYSI86Ngx6BWCi5UlVQHcUYjP0HPbDONGycD6fYJN75TAYfDeWptFcYM8zDdpZTaXfwg4s9KXJBKJl" http://localhost:8000/o/token/
    
    {"access_token": "<access_token>", "token_type": "Bearer", "expires_in": 60, "refresh_token": "<refresh_token>", "scope": "transact view"}
    
## Authorization

The CoinsWallet API allows, and in some cases requires, requests to include an access token to authorize elevated client privileges. Pass the access token via the standard `Authorization` HTTP header as type `Bearer`.

    curl -H "Authorization: Bearer <access_token>" https://localhost:8000/api/v1/endpoint/

## Schema

In production all API access should be over HTTPS. All data is sent and received as `JSON`.

> request body contains a `success` parameter which is `true/false`, and a `message` parameter.
 
>      Sample response: 
       {
          "success": true,
          "message": "Account list retrieved"
        }
        
## Pagination

All GET endpoints support pagination. Responses from such endpoints contain `meta` in the response body:
 
>       "meta": {
          "total_count": 14,
          "next_page": 3,
          "previous_page": 1
        }

To paginate a response, the following parameters should be provided:

- `page` - Page number of the result set.

- `per_page` - Optional. The number of items to return per page. Defaults to 10 and allows up to 100.


    Example:
    curl -H "Authorization: Bearer {access_token}" https://localhost:8000/api/v1/accounts/?page=2&per_page=5


## API Endpoints

#### 1. List of accounts registered:
> GET api/v1/accounts/

>       GET /api/v1/accounts/?page=1&amp;per_page=5 HTTP/1.1
        Host: localhost:8000
        Authorization: Bearer 5KMNBDbKIsirEJBrCbp74EhTULVwlg
        
        Sample response:
        {
          "success": true
          "message": "Account list retrieved",
          "meta": {
            "total_count": 14,
            "next_page": 2,
            "previous_page": 1
          },
          "accounts": [
            {
              "id": 1,
              "owner": "kaushal",
              "balance": 441,
              "currency": "PHP"
            },
            {
              "id": 2,
              "owner": "sapan",
              "balance": 59,
              "currency": "PHP"
            }
          ],
        }


#### 2. Payment: transfer amount from one account to other:
> POST api/v1/payments/

>       POST /api/v1/payments/ HTTP/1.1
        Host: localhost:8000
        Authorization: Bearer 5KMNBDbKIsirEJBrCbp74EhTULVwlg
        Content-Type: application/json
        {
            "from_account":"1",
            "to_account":"2",
            "amount": 9
        }
        
        Sample response::
        {
            "message": "Payment successful",
            "success": true
        }
        
#### 3. Payment: get list of transactions:
Fetch list of transactions for the user authenticated with access_token
> GET api/v1/payments/

>       GET /api/v1/payments/?page=1&amp;per_page=10 HTTP/1.1
        Host: localhost:8000
        Authorization: Bearer 5KMNBDbKIsirEJBrCbp74EhTULVwlg
        
        Sample response::
          {
              "message": "transactions list",
              "meta": {
                "total_count": 13,
                "next_page": 2,
                "previous_page": 1
              },
              "success": true,
              "transactions": [
                {
                  "id": 14,
                  "amount": 9,
                  "currency": "PHP",
                  "direction": "outgoing",
                  "debit_from": "kaushal",
                  "credit_to": "sapan",
                  "created": "2017-04-10T08:24:55.599119Z"
                },
                {
                  "id": 13,
                  "amount": 9,
                  "currency": "PHP",
                  "direction": "outgoing",
                  "debit_from": "kaushal",
                  "credit_to": "sapan",
                  "created": "2017-04-09T10:28:20.914000Z"
                }
              ]
            }
  
## Errors

There are the most common errors a client may receive when calling the API.

1. Sending misspelled or improperly formatted request bodies or querystring parameters will result in a `400 Bad Request` response.
    
    ```http
    HTTP/1.1 400 Bad Request
    Content-Type: application/json; charset=utf-8

    {
        "success": false,
        "message": "Invalid request, parameters missing"
    }
    ```

2. Sending same transaction request twice is not permitted in certain time frame.
Same transaction request is accepted only after 10 minutes or new `access_token` is issued before that.
    
    ```http
    HTTP/1.1 400 Bad Request
    Content-Type: application/json; charset=utf-8
    {
        "message": "Same transaction restricted twice, please retry after 10 minutes",
        "success": false
    }
    ```
