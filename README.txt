History of project is, I was making arbitrage operations between cex.io and btcturk.com (BTC markets) manually.
The gap was so good thus even manually i made a good amount of money.
But later the gap between market got lower and I decided to write a arbitrage bot that waits for a reasonable gap to occur and take necessary buy / send / sell operations between markets. This is how this project came to life. There were many open source arbitrage bots in the market but I wanted to learn Python and write my own code that is capable of making operation in Turkish market also. Thats why I didn't use other bots.
That time I was working as an Embedded Engineer at Airties. After 4 months the bot was working and I started to earn money. Since it was my first Python project, during the time I got better python knowledge  and decided to go further by adding other markets. I also refactored the whole project and implemented it from scratch .

In this refactoring,
I created an event base (consumer & producer) transaction engine in the heart of the project. This engine is responsible for operating created transactions(buy/sell/send/seek prices and etc.). If any error occur during the transaction this engine tries again the operation until a threshold before canceling the transaction. After the transaction is completed , this engine notifies the registered consumers(where transactions is created and added to transaction list to operate) with event.
Transaction Engine : https://github.com/ozanOzenoglu/arbitrage-hero/blob/main/base/crypto_engine/engine/transaction_engine.py
I created thread base services that consumes json event and take responsible action whenever they receive an event.
These are the all services: https://github.com/ozanOzenoglu/arbitrage-hero/tree/main/base/services
I'd like to explain a few of them.
But before explaining services There are really two important classes that has all common functionality of all services and expose these common functionality to all services based on parent-child relationship. These are IWatchableService and IWatchableWatcherService classes.

i_watchable_service.py: This is the base class for all services. Even in python there is no interface mechanism like in Java or C#, I designed this class as an interface that has two methods . Init method and start method. This class check child classes if they implemented these methods other wise raise an exception.So every child class that is inherited from this class must implement these two methods.
The goal of this base class is providing a WatchDog mechanism for derived class. If derived sub classes(service classes) some how interrupted or exited they automatically re-start themselves until a threshold. Threshold is usually infinite. https://gitlab.com/kozmotr2/DARPHANE/-/blob/master/base/services/i_watchable_service.py

IWatchableWatcherService.py : This is another an interface-like class that is inherited from i_watchable_service.py.So it implements init and start method since it's inherited from i_watchable_service.py and introduce two new methods as interface methods. parse_file and action.
Every services that is inherited from IWatcableWatcherService.py must implement their own parse_file and action methods. parse_file is basically for parsing event that service consumes.Since event might be different for different services, parsing them should be taken differently. And different services do different jobs their action for events should be different. So services must implement their own action and parse_file methods. Besides, IWatchableWatcherService provides a common functionality in its start method. So it listens events , parse them by using sub-services parse_file method , store them into waiting events list and iterate over them and invoke action method of child classes. So I didn't have to re-implement every time this functionality in every services.

I tried to collect common behaviors of all services into these two interface like class. One of them is WatchDog functionalty . And other is listen a folder for json based events, parse them and take necessary action for events.


Services:

StatisticService.py : This service consumes event that holds the information of current status of markets and their prices which is created by other services.
And it is taking record of all market prices and the gap between all currencies and store them. So my android application can show a historical data with a Chart representation. This feature usually does not exits in other arbitrage bots.
So an user can see , when an arbitrage opportunity was occured and how much the gap it is up to one month.

TableService.py :
Table service is responsible for creating table charts in svg format. So user can see a time chart that shows arbitrage opportunities in the market.

SimulatorService.py
This service is doing fake buy/send/buy operations for arbitrage opportunities and calculates the money earned from the opportunity.

ob_service.py(OrderBookService):
This service is collecting currency prices from markets and store them into the database.

op_finder_service.py :
This service reads configuration data and start sub-threads for every market/currency pair in configuration. For every pair a sub-thread is created that monitors
for a possible arbitrage opportunity for given market and currency pairs.

OB_Fresh_Guard_Service:
This service is responsible for keep data fresh. For somehow an information in database related to prices in markets is old. This service
push a request to related market service to fetch and update the data.

OrderBookFetcherService.py:
This is another giant service. In the past , some markets were not providing rest apis to outside world. Thats why I had to implement selenium based this service. With selenium , I login markets and parse the html and obtain necessary information from markets like currency pairs, prices and so on. Afterwards I refactored this service to handle buy / sell / withdraw and deposit actions. There was a Turkish market named koineks. I was tricking this market with this service , like an actual person doing all operation over web browser. This service was capable of login, parsing sms-authentication code , and do all action a person can make on a market via web browser. But then market got closed and this service is abandoned.

Note: This service is heavily use all parallel-programing approaches in modern programming languages. From barriers to mutex and much more. It even determines the optimum thread number that this service can run on a system. It makes a performance test and determines the optimum thread count.

LoadBalancer.py:
This is a task-dispatcher service for OrderBookFetcherService.py. Since there are a lot of running threads under OrderBookService.py , all of them are acting as a separate service. LoadBalancer detects which service is busy, which service is not and dispatch to job to the available service.

btcturk_service.py:
Btcturk does not provide all restfull api to outside world. Especially for withdraw the money. For these kind of operations, this is another selenium based service. Listens request and take necessary action on web browser for Btcturk Market such as withdraw the money.

--- End of Services ---

https://github.com/ozanOzenoglu/arbitrage-hero/tree/main/server

Under this folder you may find my restfull apis.
When I was writing this I didn't know Django or Flask Python Framework. Thus I use Core HttpServer class to provide restfull api to my android application.

https://github.com/ozanOzenoglu/arbitrage-hero/tree/main/base/crypto_engine/browser

Under this folder, you may find classes that I implemented for selenium based browsers for taking actions on related markets.
My plan was providing an common browser class that is used actions handlers to take necessary operation on markets.
Since every market front end is different I have to implement different browser classes.
This browser classes are used by handler services, so I have a common handler service and different browser classes.

You may find handler services are here :
https://github.com/ozanOzenoglu/arbitrage-hero/tree/main/base/crypto_engine/request_handler

Thank you for your time.
