import type { Puzzle } from "../types";
import { makePuzzle } from "./helpers";

const family = (answer: string, clue: string, fact: string, difficulty: 1 | 2 | 3): Puzzle =>
  makePuzzle("families", answer, clue, fact, difficulty);

export const FAMILIES: Puzzle[] = [
  family(
    "COPPOLA",
    "The Godfather director, his Lost in Translation daughter, and actor Nicolas Cage share this family name.",
    "Francis Ford Coppola's daughter Sofia became a director, and Nicolas Cage is his nephew.",
    2,
  ),
  family(
    "FONDA",
    "Henry, Jane, and Peter are three generations of this acting family.",
    "Henry, Jane, and Peter Fonda all earned Oscar nominations; Bridget Fonda continued the acting line.",
    2,
  ),
  family(
    "DOUGLAS",
    "Kirk, Michael, and Cameron are three generations of this acting dynasty.",
    "Michael Douglas won Best Actor for Wall Street, while Kirk received an honorary Oscar.",
    2,
  ),
  family(
    "BARRYMORE",
    "Drew and her grandparents John and Ethel share this famous acting surname.",
    "John, Ethel, and Lionel Barrymore were celebrated stage and screen stars.",
    2,
  ),
  family(
    "BALDWIN",
    "Alec, Daniel, William, and Stephen are four acting brothers with this last name.",
    "The brothers have worked across film, television, and stage for decades.",
    1,
  ),
  family(
    "SHEEN",
    "Martin and his sons Emilio and Charlie are part of this acting family.",
    "Martin Sheen was born Ramón Estévez; Emilio uses Estevez, while Charlie performs as Sheen.",
    2,
  ),
  family(
    "SKARSGARD",
    "Stellan and sons Alexander, Bill, and Gustaf share this Swedish acting surname.",
    "Alexander starred in Big Little Lies, Bill in It, and Gustaf in Vikings.",
    3,
  ),
  family(
    "GLEESON",
    "Brendan and sons Domhnall and Brian share this Irish acting surname.",
    "Domhnall appeared in Star Wars and Ex Machina; Brian played Ser Alliser Thorne in Game of Thrones.",
    3,
  ),
  family(
    "CUSACK",
    "John and his sister Joan share this Chicago acting surname.",
    "The siblings have appeared in dozens of films and occasionally acted together.",
    2,
  ),
  family(
    "ARQUETTE",
    "Patricia, Rosanna, David, and Alexis are siblings in this acting family.",
    "Patricia won Best Supporting Actress for Boyhood.",
    2,
  ),
  family(
    "WILSON",
    "Owen, Luke, and Andrew are three acting brothers with this surname.",
    "Owen and Luke frequently collaborated with director Wes Anderson.",
    2,
  ),
  family(
    "VOIGHT",
    "Jon and his daughter Angelina are part of this acting family.",
    "Jon Voight won Best Actor for Coming Home; Angelina Jolie uses her middle name.",
    2,
  ),
  family(
    "HUSTON",
    "John, son Danny, and granddaughter Anjelica form three generations of this film family.",
    "John and Anjelica Huston both won acting Oscars.",
    3,
  ),
  family(
    "REDGRAVE",
    "Vanessa and her siblings Lynn and Corin share this acting surname.",
    "Vanessa's daughters Natasha and Joely Richardson also became actors.",
    3,
  ),
  family(
    "CULKIN",
    "Macaulay and his brother Kieran share this surname.",
    "Macaulay starred in Home Alone; Kieran won an Oscar for A Real Pain.",
    2,
  ),
  family(
    "GYLLENHAAL",
    "Jake and his sister Maggie share this acting surname.",
    "Both siblings have earned Oscar nominations.",
    2,
  ),
  family(
    "FANNING",
    "Dakota and her younger sister Elle share this surname.",
    "Both sisters began acting as children and have worked in film and television.",
    1,
  ),
  family(
    "HEMSWORTH",
    "Chris, Liam, and Luke are three acting brothers with this Australian surname.",
    "Chris plays Thor, Liam starred in The Hunger Games, and Luke appeared in Westworld.",
    2,
  ),
  family(
    "HOWARD",
    "Ron and his daughter Bryce Dallas share this directing-and-acting surname.",
    "Ron directed Apollo 13 and A Beautiful Mind; Bryce starred in Jurassic World.",
    2,
  ),
  family(
    "WAYANS",
    "Keenen, Damon, Marlon, and Shawn are part of this comedy family.",
    "Keenen created In Living Color, and the family has produced films and sitcoms together.",
    2,
  ),
  family(
    "STILLER",
    "Jerry and his son Ben share this comedy surname.",
    "Ben directed Zoolander and Tropic Thunder; Jerry was half of the comedy duo Stiller and Meara.",
    2,
  ),
  family(
    "PENN",
    "Sean and his brother Chris share this acting surname.",
    "Sean won Best Actor for Mystic River and Milk.",
    2,
  ),
  family(
    "OLSEN",
    "Elizabeth and her older sisters Mary-Kate and Ashley share this surname.",
    "Elizabeth played the Scarlet Witch; her sisters starred in Full House as children.",
    1,
  ),
  family(
    "PALTROW",
    "Gwyneth and her mother Blythe Danner are part of this acting family.",
    "Gwyneth won Best Actress for Shakespeare in Love; her father was producer Bruce Paltrow.",
    3,
  ),
  family(
    "QUAID",
    "Dennis and his brother Randy share this acting surname.",
    "Dennis won Best Supporting Actor for The Right Stuff.",
    2,
  ),
  family(
    "BRIDGES",
    "Jeff, his brother Beau, and their father Lloyd share this acting surname.",
    "Jeff won Best Actor for Crazy Heart, and Lloyd earned an Oscar nomination for The Last Picture Show.",
    2,
  ),
  family(
    "WAHLBERG",
    "Mark and his older brother Donnie share this surname.",
    "Donnie found fame with New Kids on the Block; Mark starred in Boogie Nights and The Departed.",
    2,
  ),
  family(
    "HAWN",
    "Goldie and her children Kate and Oliver Hudson are part of this acting family.",
    "Goldie Hawn won an Oscar for Cactus Flower; Kate Hudson was nominated for Almost Famous.",
    3,
  ),
  family(
    "REINER",
    "Carl and his son Rob share this comedy surname.",
    "Carl Reiner created The Dick Van Dyke Show; Rob directed When Harry Met Sally.",
    2,
  ),
  family(
    "MURPHY",
    "Eddie and his older brother Charlie share this comedy surname.",
    "Eddie became an SNL star; Charlie is also an actor and comedian.",
    2,
  ),
];
