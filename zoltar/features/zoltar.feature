Feature: As a player of Zoltar
    I wish to receive a fortune
    By getting a coin into the 
    slot of Zoltar's mouth

    Background: 
        Given the game is running

    Scenario: The game has just started
        When the game begins
        Then the head should begin moving up and down

    Scenario: The coin lands in Zoltar's mouth
        When the coin lands in the mouth
        Then Zoltar's eyes pulse four times
        And A fortune is randomly selected
        And Zoltar prints out the fortune
        And The next game is triggered

