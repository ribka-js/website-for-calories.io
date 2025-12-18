const CALORIE_DATABASE = {
  // Фрукты
  apple: 52, banana: 89, orange: 47, strawberry: 32, grapes: 69,
  watermelon: 30, pineapple: 50, mango: 60, pear: 57, peach: 39,
  kiwi: 61, cherry: 50, blueberry: 57, raspberry: 52, lemon: 29,
  avocado: 160, pomegranate: 83, coconut: 354, fig: 74, plum: 46,
  apricot: 48, grapefruit: 42, lime: 30, melon: 34, blackberry: 43,
  
  // Овощи
  carrot: 41, potato: 77, tomato: 18, cucumber: 15, onion: 40,
  pepper: 31, broccoli: 34, cauliflower: 25, spinach: 23,
  lettuce: 15, cabbage: 25, zucchini: 17, eggplant: 25, pumpkin: 26,
  corn: 86, beans: 31, asparagus: 20, mushroom: 22, garlic: 149,
  ginger: 80, beetroot: 43, radish: 16, celery: 14,
  
  // Мясо и рыба
  chicken: 165, beef: 250, pork: 242, fish: 206, salmon: 208,
  tuna: 184, shrimp: 99, egg: 155, bacon: 541, sausage: 301,
  turkey: 189, lamb: 294, duck: 337,
  
  // Молочные продукты
  milk: 42, cheese: 402, yogurt: 59, butter: 717, cream: 345,
  icecream: 207, cottage_cheese: 98, sour_cream: 193,
  
  // Хлеб и выпечка
  bread: 265, croissant: 406, bagel: 289, muffin: 265, donut: 452,
  cake: 379, cookie: 502, pizza: 266, pasta: 131, rice: 130,
  
  // Напитки
  coffee: 0, tea: 1, juice: 45, soda: 41, beer: 43, wine: 83,
  
  // Разное
  chocolate: 546, nuts: 607, honey: 304, sugar: 387, oil: 884,
  mayonnaise: 680, ketchup: 101, mustard: 66
};

function findCalorieMatch(label) {
  const lowerLabel = label.toLowerCase();
  
  for (const [food, calories] of Object.entries(CALORIE_DATABASE)) {
    if (lowerLabel.includes(food) || food.includes(lowerLabel.split(' ')[0])) {
      return calories;
    }
  }
  
  const keywords = {
    'burger': 295, 'sandwich': 250, 'salad': 35, 'soup': 38,
    'fries': 312, 'chips': 536, 'candy': 380, 'popcorn': 387,
    'cereal': 379, 'oatmeal': 68, 'pancake': 227, 'waffle': 291
  };
  
  for (const [keyword, calories] of Object.entries(keywords)) {
    if (lowerLabel.includes(keyword)) {
      return calories;
    }
  }
  
  return null;
}