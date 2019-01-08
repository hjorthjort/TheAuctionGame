from src.Auction import *

courses = {
    'single_item': [Course(capacity=1, name="single_item")],
    'three_courses': [Course(capacity=3, name="physics"),
                      Course(capacity=18, name="cryptography"),
                      Course(capacity=6, name="neural networks"),
                      ]
}

# Default clearing function is a first-price.
fixed_auctions = {
    'first_price': Auction(
        clearing_function=first_price_clearing_function,
        max_bid=math.inf,
        courses=courses['single_item'],
        players=[
            Player(utilities={courses['single_item'][0]: 2.0}),
            Player(utilities={courses['single_item'][0]: 4.0}),
            Player(utilities={courses['single_item'][0]: 1.0})
        ]
    ),

    'second_price': Auction(
        clearing_function=second_price_clearing_function,
        max_bid=math.inf,
        courses=courses['single_item'],
        players=[
            Player(utilities={courses['single_item'][0]: 2.0}),
            Player(utilities={courses['single_item'][0]: 4.0}),
            Player(utilities={courses['single_item'][0]: 1.0})
        ]
    ),
    'realistic1': Auction(
        clearing_function=second_price_clearing_function,
        max_bid=50,
        courses=courses['three_courses'],
        players=[
            Player(utilities=dict([(courses['three_courses'][i], random.random()*200) for i in [0,1,2]]))
            for _i in range(20)
        ]
    )
}

