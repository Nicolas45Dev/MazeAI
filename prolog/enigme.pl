% Remove the crystal based on the number of crystals and the color of the lock
remove_crystal(Crystals, LockColor, PositionString) :-
    length(Crystals, NumberOfCrystals),
    choose_crystal(NumberOfCrystals, Crystals, LockColor, Position),
    position_to_string(Position, PositionString).

% Convert numerical position to string
position_to_string(1, "first").
position_to_string(2, "second").
position_to_string(3, "third").
position_to_string(4, "fourth").
position_to_string(5, "fifth").
position_to_string(6, "sixth").

% Rules for three crystals
choose_crystal(3, Crystals, _, Position) :-
    (   \+ member(red, Crystals) -> Position = 2
    ;   last(Crystals, white) -> find_last_position(white, Crystals, Position)
    ;   count(blue, Crystals, Count), Count > 1 -> find_last_position(blue, Crystals, Position)
    ;   Position = 1
    ).

% Rules for four crystals
choose_crystal(4, Crystals, LockColor, Position) :-
    (   count(red, Crystals, CountRed), CountRed > 1, LockColor == silver -> find_last_position(red, Crystals, Position)
    ;   last(Crystals, yellow), \+ member(red, Crystals) -> Position = 1
    ;   count(blue, Crystals, 1) -> Position = 1
    ;   count(yellow, Crystals, CountYellow), CountYellow > 1 -> find_last_position(yellow, Crystals, Position)
    ;   Position = 2
    ).

% Rules for five crystals
choose_crystal(5, Crystals, LockColor, Position) :-
    (   last(Crystals, black), LockColor = gold -> Position = 4
    ;   count(red, Crystals, 1), count(yellow, Crystals, CountYellow), CountYellow > 1 -> Position = 1
    ;   \+ member(black, Crystals) -> Position = 2
    ;   Position = 1
    ).

% Rules for six crystals
choose_crystal(6, Crystals, LockColor, Position) :-
    (   \+ member(yellow, Crystals), LockColor == bronze -> Position = 3
    ;   count(yellow, Crystals, CountYellow), CountYellow = 1, count(white, Crystals, CountWhite), CountWhite > 1 -> Position = 4
    ;   \+ member(red, Crystals) -> Position = 6
    ;   Position = 4  % Default action if none of the above conditions are met
    ).

% Count the number of occurrences of an element in a list
count(Element, List, Count) :-
    aggregate_all(count, member(Element, List), Count).

% Find the position of the last crystal of a specific color in the list
find_last_position(Color, List, Position) :-
    reverse(List, ReversedList),
    nth1(Pos, ReversedList, Color),
    length(List, Length),
    Position is Length - Pos + 1.