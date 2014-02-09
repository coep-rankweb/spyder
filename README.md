Spyder
-------------------

A simple scrapy based webcrawler

Stores its data into a mongodb database via the following collections:

     collection URL_DATA
     {
          id: 24
          url: "http://www.example.com"
          word_vec: ["example", "word", "trial", "placeholder"]
     }


     collection WORD_DATA
     {
          id: 24
          word: "example"
          present_in: [24, 32, 92]
     }

     collection CRAWLER_DATA
     {
          POWER_SWITCH: "ON"
     }
