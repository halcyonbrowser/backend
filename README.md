# ☄️ Halcyon (Backend)

> A cross-platform browser for the elderly and the visually impaired - paired with both automated artificial intelligence and customized human operator service!


## Purpose
Our backend REST-ful API server is in charge of doing all sorts of computational conveniences for our cross-platform desktop browser meant for the elderly and the visually impaired.

Main tasks by the API server are:
* **Process an audio file**, decode it to its textual counterpart and fire the relevant task as intended by the user
* **Allow for two-way audio streaming/chat**, allowing a remote human operator to service a user along for his/her internet browsing experience needs.
* **Analyze a webpage**, rank textual content/summaries accordingly and provide a pleasing filtered result out of the plethora of information available on a site for the browser to present.
* **Facilitate for a modified and friendly way to access Facebook**, allowing important tasks such as timeline traversal, posting a status, checking notifications or sending/reading messages to be accessible to the end user.

## Tech Stack
Deploying on a Linode server on a Docker-ized environment consisting of:
* 🐍 **Python 2.7** - Main programming language of choice
* 🐋 **Docker** - Containerization and easy dev/prod setup
* 🎓 **Stanford CoreNLP** - POS, NER, Dependency Parsing and all NLP utilities, made easy (Stanford university research project)
* 🔬 **Flask** - Simple HTTP API server DSL
* 🗒️ **Postgres** - Primary datastore (to make our NLP estimations "smarter")
* 🐛 **Apache Kafka** - For creating streams of requests and responses - getting those Big Data points for streaming out user-provided and machine output data!

## DB Schema
Our Postgres database sports the following data schema - database tables followed by the database column types:
* **session** - id:int, time:time, os:string, cpu_count:int, release:string, hostname:string
* **command** - id:int, session_id:int(foreign), command:string(goto, goto_full, search, login_facebook)
* **document** - id:int, website:string
* **document_atom** - document_id:int(foreign), rank:int, text:string, type:string(highlight, image_description, factoid, link), entity:string(person, organization, location, money, percent, date, time)

## API Endpoints
* POST _/init/_ 
  * Request: `json` - device-identifying information, stored under `devid` key
    
    ```
    {
      os: string,
      cpu_count: string,
      release: string,
      hostname: string
    }
    ```
  
  * Response: `string` - token that can be paired with subsequent command-based API requests to co-identify a command to a session (for smarter summaries and actions)
 
* POST _/command_audio/_
  * Request: `multipart/form-data` - audio file to process (recorded user's speech) uploaded in an upload form with key `command` and token with key `token`
  * Response: `json` 
  
    ```
    {
      command_type: "goto"|"goto_full"|"goto_link"|"search"|"login_facebook",
      result: SearchResultList|{}
    }
    ```
    
    If the command_type is "search", a result of schema `SearchResultList` is returned as the `result`'s value. Otherwise, an empty object is returned. `SearchResultList` has the following schema:
    
    ```
    [{
      doc_id: int,
      rank: int,
      type: string,
      entity: string,
      text: string
    }]
    ```

* POST _/command/_
  * Request: `string` - command type, stored under `command` key
  * Response: same as `POST _/command_audio/_`'s response logic
