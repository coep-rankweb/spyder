Spyder
-------------------

A simple scrapy based webcrawler

Stores its data into a mongodb database via the following collections:

     collection URL_DATA
     {
          id: 24
          url: "http://www.example.com"
          word_vec: [32, 16, 88]
     }


     collection WORD_DATA
     {
          id: 16
          word: "example"
          present_in: [24, 32, 92]
     }

     collection CRAWLER_DATA
     {
          POWER_SWITCH: "ON"
     }
