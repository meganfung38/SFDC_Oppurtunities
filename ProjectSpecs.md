# Project Design Specs: SFDC Opportunities Analysis Report

This document outlines the roadmap and external dependencies required to implement a solution for analyzing Salesforce opportunities.



## Problem Statement 

Salesforce opportunities are critical for tracking the sales pipeline and decision-making processes. However, the current system lacks meaningful insights into opportunity outcomes:


- __Stage: 0. Downgraded__
  - Downgrade Reason field: often contains vague or unhelpful information (ex. "Not BANT qualified"), failing to provide actionable insights into why opportunities were downgraded.
  - This limits the ability to understand and address root causes of lost opportunities.

    
- __Stage: 7. Closed Won__
  - Win Reason field: sparsely populated or left blank, offering little insight into what factors contributed to successfully closed deals.
  - As a result, the sales team struggles to replicate success and optimize sales strategies.

Additionally, __call logs__ between sales reps and customers-- which could provide valuable insights-- are not currently tied back to SFDC opportunities.



## Objective 

The project aims to connect SFDC opportunity data with sales call insights and:
- Extract relevant SFDC opportunities from Hadoop.
- Retrieve corresponding sales call recordings from RingSense.
- Leverage AI to analyze call data and SFDC fields, identifying patterns, sentiment, and decision-making trends.
- Generate actionable insights to improve sales performance and decision-making.




# Proposed Solution 



## Dependencies/ Needed Sources


- __Hadoop__
  - Access Request: JIRA Ticket ([sample ticket](https://jira.ringcentral.com/browse/OPS-378891))
    - Requires RC VPN for cluster access.
  - Purpose: Query the `sfdc_production.opportunity` table to collect SFDC opportunities.

    
- __RingSense__
  - Access Request: FreshService Ticket ([sample ticket](https://ringcentral.freshservice.com/support/tickets/1685796))
    - Requires admin license (contact the Sales Enablement team).
  - Purpose: Access an organized platform containing call logs between sales reps and customers, allowing easy filtering by company.

    
- __RingCentral Developers__
  - RingCX API Endpoint (__PENDING: endpoint in development__)
    - [deprecated endpoint](https://developers.ringcentral.com/engage/voice/guide/analytics/reports/global-call-type-detail-report)
  - RingSense API Endpoint
    - [getRecordingInsights endpoint](https://developers.ringcentral.com/api-reference/RingSense/getRecordingInsights)

      
- __OpenAI__
  - Requirement: Purchase a OpenAI API key
  - Purpose: Use OpenAI to generate AI-driven insights and trend reports.



## Tech Stack 


- __Programming Language__: Python

  
- __Libraries:__
  - Data integration: `impala.dbapi`, `ringcentral`, `openai`
  - Data organization: `pandas`



## Files 


__SFDC_Data.py__: Hadoop Data Integration 


__RingSense_Analytics.py__: RingSense Insights Integration (for call logs) 


__Generate_Report.py__: AI Integration



## Configuration


**Setting up Your Virtual Environment**


1. Activate a virtual environment (depending on machine instructions will vary)
   
   ```bash
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

   
2. install dependencies in requirements.txt

   ```bash
   pip install -r requirements.txt
   ```

   
**Setting up OpenAI**


3. Create a file called `config.py`. Provide your OpenAI API key secret in this file.

   ```python
   OPENAI_API_KEY='<API KEY SECRET>'
   ```

   *add `config.py` your `.gitignore` file to protect the key*


4. Export the OpenAI API key to your virtual environment

   ```bash
   export OPENAI_API_KEY='<API KEY SECRET>'
   ```

   
**Setting up Connection to Hadoop Hive Cluster**


5. Enable the kerberos client

   ```bash
   kinit <RC email>
   ```

   
6. Instaniate a Hive ticket

   ```bash
   kinit -S hive/hiveserver.ringcentral.com <RC email>
   ```

   
7. Confirm that the Hive ticket was successfully created using `klist`
   
   <img width="652" alt="Screenshot 2024-11-29 at 1 45 49 PM" src="https://github.com/user-attachments/assets/aecf0ba7-ba1d-499b-b3cd-8007e91708cf">

 

## Backend Implmentation 


**1. Extract SFDC Opportunities**
__SFDC_Data.py__

   - Use Hadoop to query opportunities
   
   ```sql
   SELECT *
   FROM opportunity
   WHERE stagename = '7. Closed Won'; 
    
   SELECT *
   FROM opportunity
   WHERE stagename = '0. Downgraded';
   ``` 


**2. Identify Call Logs**

   - Reccomended Approach:
     
     a. Run a sample report of SFDC opportunities and gather a list of companies we've closed deals with or downgraded.

     <img width="1417" alt="Screenshot 2024-11-29 at 12 34 11 PM" src="https://github.com/user-attachments/assets/9a41e086-802d-4463-9d43-7221dd7cc018">
      
     b. In Ringsense, filter call logs for the list of companies gathered. The "Source" field will tell you what RC product is being used to host the call log-- where the call log is saved. 

     <img width="1434" alt="Screenshot 2024-11-29 at 12 40 11 PM" src="https://github.com/user-attachments/assets/3dc9d3f8-55d8-4055-9496-a49619976422">
     
     c. Complete a few iterations of this process to identify where call logs are being saved. 
   
   - Generally, since sales reps use AutoDialer or manual dialing in RCX/ Buddy Tool, call logs will be saved in the RingCX API.


     
**3. Retrieve Source Ids**

   - Assuming most call logs are saved in RingCX, go to the API reference for RingCX.
     - __Currently the endpoint that would be used to retrieve the sourceRecordIds for call logs in RingCX has been deprecated and is in actively being developed__: [deprecated endpoint](https://developers.ringcentral.com/engage/voice/guide/analytics/reports/global-call-type-detail-report)
     - Once this endpoint is deployed, the property to target in the API response is `sourceId`
   
   - For call logs saved elsewhere, use the API reference in the RingCentral Developers Portal to find an endpoint that will return the call log's `source id`.


     
**4. Isolate the the API response retrieved in the previous step to map a list containing the following fields:**

   - `sourceId`-- sourceRecordId of call log
     
   - Figure out which field contains information about what company/ name of person called
     - Potential fields to consider: `sourceGroupName`, `sourceName`, `connectedName`
       
   - `dnis`-- dialed number of call log
     
   - `callDuration`-- filter for calls with duration greater than 5 minutes to target calls that actually contain meaningful discussion
     
     ```json
     [
         {
             "sourceId": 33333,
             "dnis": "4155550100",
             "callDuration": 35,
         }
     ]
     ```


     
**5. Join SFDC Data with Call Log Data**

   - Join call logs to SFDC opportunities:
     - Match `sfdc_production.opportunity.name` with `company name` in call log data.
     - Match `sfdc_production.opportunity.partner_contact__c` with `dnis` in call log data.
       
   - This step essentially maps relevant call logs back to to sales reps and SFDC opportunities.


     
**6. Retrieve Call Insights**
__RingsenseAnalytics.py__

   - Call the getRecordingInsights endpoint for each sourceId in the joined table of data. 
     - [Endpoint Guide in RingCentral Developers](https://developers.ringcentral.com/api-reference/RingSense/getRecordingInsights)
     - Endpoint Path Parameters:
       
       ```json
         [
             {
                 "accountId": "~",
                 "domain": "pbx",
                 "sourceRecordId": <for each SFDC opportunity, set to its corresponding "sourceId">
             }
         ]
         ```
       
     - NOTE: depending on where the call log was hosted, this endpoint may or may not return a response. For sourceIds saved in RingCX and RingEX, a response is expected to return. However, for other sources such as Microsoft Teams, RingCentral Phone, and RingCentral Video, a response may not return. For more information contact a RC employee listed at the bottom of this file.


    
**7. Data Organization**

  - Organize the gathered data. A suggested table schema is below:
    
    
   | sfdc_production.opportunity.name | sfdc_production.opportunity.stagename | RingSenseData |
   |----------------------------------|---------------------------------------|---------------|
   |      JPC Property Management     |            7. Closed Won              |      <Data>   |




**8. Analyze With OpenAI**
__Generate_Report.py__

  - Use the ask_openai() function analyze the SFDC opportunity data and RingSense insights data using OpenAI
      
      ```python
      # context for pre-processing
      documentation = <relevant information for LLM to process before request>

      # provide a brief description of each RC_product
      RC_products = <relevant information for LLM to process before request>

      # define a set of directions for how LLM should process data gathered
      system_prompt = <relevant information for LLM to process before request>

      full_request = documentation + RC_products + system_prompt

      # SFDC opportunity call log data 
      user_prompt = <gathered SFDC opportunity call log data (table from step 8)>
      
      ask_openai(client, full_request, user_prompt)
      ```




# Contacts

List of people who can lend a helping hand in clarifying pieces of this project.



## Project Spec

Natalie Ryan



## Hadoop

Renz Joshua Burce, Ericson Marcos, Fatima Coleen Cuyco


## RC VPN Configuration

Ibrahim Wahba



## RingCentral Developer API Endpoints

  - Prashant Kukde: General 
  - Steve Yip: General
  - Shantanu Kulkarni: General
  - Sameep Lad: General
  - Jeba Thanaraj: Progress on RingCX endpoint development
  - Oscar Santiago Jr: Call log data, RingCX, Hadoop
  - Hari Srinivasan: Help with importing endpoints in local instance of Postman for endpoint testing, additional information regarding endpoints and access
    



# Megan's Weekly Updates 
[Doc with Weekly Updates](https://docs.google.com/document/d/11Az4Z2UFS48wQMwv_6t7hGgA2ZDejFLof5hI7aUeVPU/edit?usp=sharing)
*may be helpful for whoever takes over this project*
