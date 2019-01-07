from src.Auction import *

courses = {
    'first_price': [Course(capacity=1, name="first_price")]
}


# Default clearing function is a first-price.
fixed_auctions = {
    'first_price': Auction(
        clearing_function=first_price_clearing_function,
        max_tokens=math.inf,
        courses=courses['first_price'],
        players=[
            Player(utilities={courses['first_price'][0]: 2.0}),
            Player(utilities={courses['first_price'][0]: 4.0}),
            Player(utilities={courses['first_price'][0]: 1.0})
        ]
    ),

    'second_price': Auction(
        clearing_function=second_price_clearing_function,
        max_tokens=math.inf,
        courses=courses['first_price'],
        players=[
            Player(utilities={courses['first_price'][0]: 2.0}),
            Player(utilities={courses['first_price'][0]: 4.0}),
            Player(utilities={courses['first_price'][0]: 1.0})
        ]
    )
}

