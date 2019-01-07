from src.Auction import *

courses = {
    'single_item': [Course(capacity=1, name="single_item")]
}


# Default clearing function is a first-price.
fixed_auctions = {
    'first_price': Auction(
        clearing_function=first_price_clearing_function,
        max_tokens=math.inf,
        courses=courses['single_item'],
        players=[
            Player(utilities={courses['single_item'][0]: 2.0}),
            Player(utilities={courses['single_item'][0]: 4.0}),
            Player(utilities={courses['single_item'][0]: 1.0})
        ]
    ),

    'second_price': Auction(
        clearing_function=second_price_clearing_function,
        max_tokens=math.inf,
        courses=courses['single_item'],
        players=[
            Player(utilities={courses['single_item'][0]: 2.0}),
            Player(utilities={courses['single_item'][0]: 4.0}),
            Player(utilities={courses['single_item'][0]: 1.0})
        ]
    )
}

