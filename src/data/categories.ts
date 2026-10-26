import type { Category } from "../types";

export const CATEGORIES: Category[] = [
  {
    id: "movies",
    name: "Movies",
    tagline: "The big screen",
    description: "Blockbusters, cult classics, and Oscar winners.",
    icon: "clapper",
    accent: "#f4c95d",
  },
  {
    id: "tv",
    name: "TV Series",
    tagline: "The small screen",
    description: "Prestige dramas, sitcoms, and binge-worthy hits.",
    icon: "tv",
    accent: "#80d9e8",
  },
  {
    id: "actors",
    name: "Actors",
    tagline: "Leading men",
    description: "The faces who defined the movies.",
    icon: "actor",
    accent: "#f0926f",
  },
  {
    id: "actresses",
    name: "Actresses",
    tagline: "Leading ladies",
    description: "Icons, Oscar winners, and scene stealers.",
    icon: "actress",
    accent: "#f28fb6",
  },
  {
    id: "characters",
    name: "Characters",
    tagline: "Screen legends",
    description: "Heroes, villains, and unforgettable names.",
    icon: "mask",
    accent: "#b49cff",
  },
  {
    id: "directors",
    name: "Directors",
    tagline: "Behind the camera",
    description: "The visionaries who call the shots.",
    icon: "director",
    accent: "#7bd6ae",
  },
  {
    id: "families",
    name: "Film Families",
    tagline: "Hollywood dynasties",
    description: "Acting clans and famous movie relatives.",
    icon: "family",
    accent: "#ffb26b",
  },
];

export const CATEGORY_MAP = Object.fromEntries(
  CATEGORIES.map((category) => [category.id, category]),
) as Record<Category["id"], Category>;

export const DIFFICULTY_LABEL: Record<1 | 2 | 3, string> = {
  1: "Easy",
  2: "Medium",
  3: "Hard",
};
