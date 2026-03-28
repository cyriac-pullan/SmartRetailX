#!/usr/bin/env python3
"""
generate_real_products.py
Generates 1000 realistic Indian supermarket products with accurate names,
units (ml/L for liquids, g/kg for solids), and real-world pricing.
Output: database/products_unique.csv
"""
import csv, os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUT_CSV  = BASE_DIR.parent / "database" / "products_unique.csv"

FIELDNAMES = ["Product_ID","Barcode","Product_Name","Price","Weight_kg","Category",
              "Sub_Category","Aisle_No","Partition_No","Shelf_No","Position_Tag",
              "Side","Stock_Quantity","Reorder_Level"]

# Format: (Category, Sub_Category, Name, Price_INR, Weight_kg)
# For display purposes Weight_kg is used internally; unit label is in the product name.
# Liquids use ml/L in name, solids use g/kg.
PRODUCTS = [
# ── GRAINS & FLOUR ──────────────────────────────────────────────────────────
("Grains","Atta","Aashirvaad Select Sharbati Atta 5kg",275,5.0),
("Grains","Atta","Fortune Chakki Fresh Atta 10kg",430,10.0),
("Grains","Atta","Pillsbury Atta Multigrain 5kg",290,5.0),
("Grains","Atta","Rajdhani Whole Wheat Atta 10kg",410,10.0),
("Grains","Atta","Nature Fresh Sampoorna Atta 5kg",260,5.0),
("Grains","Atta","Aashirvaad Multigrain Atta 5kg",310,5.0),
("Grains","Atta","Patanjali Atta 5kg",220,5.0),
("Grains","Atta","Naturally Yours Organic Whole Wheat Atta 5kg",380,5.0),
("Grains","Flour","Fortune Maida 1kg",48,1.0),
("Grains","Flour","Pillsbury Maida 1kg",50,1.0),
("Grains","Flour","Rajdhani Besan 500g",60,0.5),
("Grains","Flour","Aashirvaad Besan 500g",65,0.5),
("Grains","Flour","Fortune Besan 1kg",115,1.0),
("Grains","Flour","Pillsbury Rava Sooji 1kg",55,1.0),
("Grains","Flour","MTR Rava Fine 500g",45,0.5),
("Grains","Flour","Aashirvaad Rava 1kg",60,1.0),
("Grains","Flour","Nature Fresh Rice Flour 500g",40,0.5),
("Grains","Flour","Fortune Rice Flour 1kg",75,1.0),
("Grains","Rice","India Gate Basmati Rice Classic 5kg",650,5.0),
("Grains","Rice","Daawat Rozana Basmati Rice 5kg",580,5.0),
("Grains","Rice","Kohinoor Silver Basmati Rice 5kg",620,5.0),
("Grains","Rice","Fortune Biryani Special Basmati 5kg",700,5.0),
("Grains","Rice","Patanjali Basmati Rice 1kg",110,1.0),
("Grains","Rice","India Gate Feast Rozzana 5kg",490,5.0),
("Grains","Rice","Daawat Super Basmati 5kg",720,5.0),
("Grains","Rice","Lal Qilla Basmati Rice 5kg",825,5.0),
("Grains","Rice","Double Horse Idli Rice 5kg",280,5.0),
("Grains","Rice","India Gate Sona Masoori 5kg",370,5.0),
("Grains","Noodles","Maggi 2-Minute Noodles Masala 70g",14,0.07),
("Grains","Noodles","Maggi 2-Minute 5-pack Masala 350g",65,0.35),
("Grains","Noodles","Yippee Classic Masala 75g",14,0.075),
("Grains","Noodles","Top Ramen Chicken 75g",14,0.075),
("Grains","Noodles","Ching's Secret Hakka Noodles 240g",70,0.24),
("Grains","Pasta","Borges Penne Rigate Pasta 500g",120,0.5),
("Grains","Pasta","Borges Spaghetti Pasta 500g",120,0.5),
("Grains","Pasta","Barilla Penne Pasta 500g",210,0.5),
("Grains","Pasta","Barilla Spaghetti 500g",210,0.5),
("Grains","Pasta","Del Monte Penne Pasta 500g",130,0.5),
("Grains","Pasta","Borges Fusilli 500g",120,0.5),

# ── PULSES & DAL ─────────────────────────────────────────────────────────────
("Pulses","Dal","Toor Dal 1kg",165,1.0),
("Pulses","Dal","Moong Dal Yellow Split 1kg",150,1.0),
("Pulses","Dal","Chana Dal 1kg",120,1.0),
("Pulses","Dal","Urad Dal White 1kg",155,1.0),
("Pulses","Dal","Masoor Dal 1kg",120,1.0),
("Pulses","Dal","Rajdhani Toor Dal 2kg",320,2.0),
("Pulses","Dal","Patanjali Moong Dal 1kg",145,1.0),
("Pulses","Dal","Fortune Toor Dal 1kg",160,1.0),
("Pulses","Dal","Bb Royal Masoor Dal 500g",65,0.5),
("Pulses","Beans","Kabuli Chana 1kg",185,1.0),
("Pulses","Beans","Rajma Red Kidney Beans 500g",90,0.5),
("Pulses","Beans","Black Eyed Peas Lobia 500g",80,0.5),
("Pulses","Beans","Green Moong Whole 500g",95,0.5),
("Pulses","Beans","Black Gram Kala Chana 1kg",110,1.0),

# ── OILS & GHEE ──────────────────────────────────────────────────────────────
("Oils","Cooking Oil","Fortune Sunflower Oil 1L",155,0.92),
("Oils","Cooking Oil","Saffola Gold Oil 1L",180,0.92),
("Oils","Cooking Oil","Dhara Refined Sunflower Oil 5L",720,4.6),
("Oils","Cooking Oil","Fortune Refined Soyabean Oil 1L",145,0.92),
("Oils","Cooking Oil","Patanjali Mustard Oil 1L",170,0.92),
("Oils","Cooking Oil","Dhara Mustard Oil 1L",180,0.92),
("Oils","Cooking Oil","Kisan Groundnut Oil 1L",195,0.92),
("Oils","Cooking Oil","Borges Extra Virgin Olive Oil 500ml",650,0.46),
("Oils","Cooking Oil","DiSano Olive Oil 1L",800,0.92),
("Oils","Cooking Oil","Saffola Active Oil 2L",340,1.84),
("Oils","Cooking Oil","Fortune Rice Bran Oil 1L",175,0.92),
("Oils","Ghee","Amul Pure Ghee 500ml",340,0.5),
("Oils","Ghee","Amul Pure Ghee 1L",660,1.0),
("Oils","Ghee","Patanjali Cow Ghee 500ml",320,0.5),
("Oils","Ghee","Mother Dairy Cow Ghee 1L",650,1.0),
("Oils","Ghee","Aashirvaad Svasti Ghee 500ml",335,0.5),
("Oils","Ghee","Gowardhan Cow Ghee 1L",690,1.0),

# ── DAIRY: MILK ──────────────────────────────────────────────────────────────
("Dairy","Milk","Amul Taaza Toned Milk 1L",66,1.0),
("Dairy","Milk","Amul Gold Full Cream Milk 1L",79,1.0),
("Dairy","Milk","Mother Dairy Full Cream Milk 1L",68,1.0),
("Dairy","Milk","Nandini Full Cream Milk 1L",62,1.0),
("Dairy","Milk","Nestle a+ Slim Milk 1L",75,1.0),
("Dairy","Milk","Amul Slim N Trim Milk 500ml",38,0.5),
("Dairy","Milk","Patanjali Cow Milk 1L",65,1.0),
("Dairy","Milk","Amul Lactose Free Milk 500ml",55,0.5),
("Dairy","Milk","Epigamia Oat Milk 200ml",35,0.2),

# ── DAIRY: PANEER, CURD, CHEESE ──────────────────────────────────────────────
("Dairy","Paneer","Amul Fresh Paneer 200g",90,0.2),
("Dairy","Paneer","Mother Dairy Paneer 200g",88,0.2),
("Dairy","Paneer","Milky Mist Paneer 200g",86,0.2),
("Dairy","Paneer","Nandini Paneer 500g",200,0.5),
("Dairy","Yogurt","Amul Masti Dahi 400g",40,0.4),
("Dairy","Yogurt","Mother Dairy Mishti Doi 200ml",35,0.2),
("Dairy","Yogurt","Epigamia Greek Yogurt Honey 90g",55,0.09),
("Dairy","Yogurt","Nestle a+ Creme Dahi 400g",50,0.4),
("Dairy","Cheese","Amul Cheese Slices 750g",450,0.75),
("Dairy","Cheese","Amul Processed Cheese Block 400g",220,0.4),
("Dairy","Cheese","Britannia Cheese Slices 750g",440,0.75),
("Dairy","Cheese","Go Cheddar Cheese 200g",180,0.2),
("Dairy","Cheese","Amul Mozzarella Cheese 200g",160,0.2),
("Dairy","Butter","Amul Salted Butter 500g",280,0.5),
("Dairy","Butter","Amul Unsalted Butter 500g",280,0.5),
("Dairy","Butter","Mother Dairy Butter 500g",275,0.5),
("Dairy","Butter","Patanjali Butter 100g",50,0.1),
("Dairy","Cream","Amul Fresh Cream 200ml",75,0.2),
("Dairy","Cream","Nestle Milkmaid Condensed Milk 400g",155,0.4),

# ── BEVERAGES: TEA ───────────────────────────────────────────────────────────
("Beverages","Tea","Tata Tea Gold 500g",290,0.5),
("Beverages","Tea","Red Label Natural Care Tea 500g",280,0.5),
("Beverages","Tea","Wagh Bakri Premium Leaf Tea 500g",250,0.5),
("Beverages","Tea","Brooke Bond Taaza Tea 500g",240,0.5),
("Beverages","Tea","Lipton Yellow Label Tea 250g",150,0.25),
("Beverages","Tea","Tata Tea Agni 1kg",420,1.0),
("Beverages","Tea","Society Tea Premium 250g",160,0.25),
("Beverages","Tea","Tetley Green Tea 100 bags",195,0.15),
("Beverages","Tea","Lipton Green Tea Honey Lemon 25 bags",125,0.04),
("Beverages","Tea","Twinings English Breakfast 25 bags",275,0.05),
("Beverages","Tea","Himalaya Tulsi Green Tea 20 bags",100,0.03),
("Beverages","Tea","Patanjali Herbal Tea 100g",90,0.1),

# ── BEVERAGES: COFFEE ────────────────────────────────────────────────────────
("Beverages","Coffee","Nescafe Classic Instant Coffee 100g",290,0.1),
("Beverages","Coffee","Bru Original Instant Coffee 100g",255,0.1),
("Beverages","Coffee","Nescafe Classic 200g",530,0.2),
("Beverages","Coffee","Bru Gold Instant Coffee 100g",330,0.1),
("Beverages","Coffee","Continental Malabar Instant Coffee 100g",290,0.1),
("Beverages","Coffee","Sunrise Special Coffee Powder 200g",195,0.2),
("Beverages","Coffee","Davidoff Rich Aroma Instant 100g",410,0.1),
("Beverages","Coffee","Nescafe Gold Blend 100g",550,0.1),

# ── BEVERAGES: JUICES ────────────────────────────────────────────────────────
("Beverages","Juice","Tropicana Orange 100% Juice 1L",120,1.0),
("Beverages","Juice","Real Fruit Power Apple 1L",100,1.0),
("Beverages","Juice","Tropicana Mixed Fruit 1L",115,1.0),
("Beverages","Juice","B Natural Mixed Fruit Juice 1L",90,1.0),
("Beverages","Juice","Real Guava Fruit Juice 1L",95,1.0),
("Beverages","Juice","Paperboat Aamras 250ml",30,0.25),
("Beverages","Juice","Paperboat Jamun Kala Khatta 200ml",25,0.2),
("Beverages","Juice","Minute Maid Pulpy Orange 400ml",30,0.4),
("Beverages","Juice","Patanjali Amla Juice 1L",110,1.0),
("Beverages","Juice","Dabur Real Pomegranate Juice 1L",135,1.0),
("Beverages","Juice","Slice Mango Drink 1L",55,1.0),
("Beverages","Juice","Maaza Mango 600ml",40,0.6),

# ── BEVERAGES: SODA & WATER ──────────────────────────────────────────────────
("Beverages","Soda","Coca Cola 750ml",44,0.75),
("Beverages","Soda","Pepsi 750ml",42,0.75),
("Beverages","Soda","Thums Up 750ml",44,0.75),
("Beverages","Soda","Sprite 750ml",42,0.75),
("Beverages","Soda","Limca 750ml",42,0.75),
("Beverages","Soda","Fanta Orange 750ml",42,0.75),
("Beverages","Soda","7Up 750ml",42,0.75),
("Beverages","Soda","Mountain Dew 750ml",44,0.75),
("Beverages","Soda","Kinley Club Soda 500ml",20,0.5),
("Beverages","Soda","Coca Cola 350ml",35,0.35),
("Beverages","Soda","Pepsi 350ml",33,0.35),
("Beverages","Water","Bisleri Mineral Water 1L",20,1.0),
("Beverages","Water","Kinley Drinking Water 1L",18,1.0),
("Beverages","Water","Himalayan Natural Water 500ml",25,0.5),
("Beverages","Water","Bisleri Mineral Water 500ml",15,0.5),
("Beverages","Energy","Red Bull Energy Drink 250ml",125,0.25),
("Beverages","Energy","Monster Energy Original 500ml",150,0.5),
("Beverages","Energy","Sting Berry Blast 250ml",25,0.25),

# ── SNACKS: CHIPS ────────────────────────────────────────────────────────────
("Snacks","Chips","Lays Classic Salted 26g",10,0.026),
("Snacks","Chips","Lays Classic Salted 52g",20,0.052),
("Snacks","Chips","Lays Magic Masala 26g",10,0.026),
("Snacks","Chips","Lays Magic Masala 52g",20,0.052),
("Snacks","Chips","Lays American Style Cream Onion 52g",20,0.052),
("Snacks","Chips","Kurkure Masala Munch 90g",20,0.09),
("Snacks","Chips","Kurkure Triangles Chatpata 90g",20,0.09),
("Snacks","Chips","Kurkure Puffcorn Yummy Cheese 60g",20,0.06),
("Snacks","Chips","Bingo Mad Angles 40g",20,0.04),
("Snacks","Chips","Bingo Tedhe Medhe 60g",20,0.06),
("Snacks","Chips","Pringles Original 107g",180,0.107),
("Snacks","Chips","Pringles Sour Cream Onion 107g",180,0.107),
("Snacks","Chips","Doritos Nacho Cheese 70g",40,0.07),
("Snacks","Chips","Doritos Cool Ranch 70g",40,0.07),
("Snacks","Chips","Too Yumm Multigrain Thins 60g",20,0.06),
("Snacks","Chips","Yellow Diamond Rings 45g",10,0.045),
("Snacks","Chips","Crax Corn Rings 50g",10,0.05),

# ── SNACKS: NAMKEEN ──────────────────────────────────────────────────────────
("Snacks","Namkeen","Haldirams Aloo Bhujia 200g",80,0.2),
("Snacks","Namkeen","Haldirams Bhujia 200g",75,0.2),
("Snacks","Namkeen","Bikaji Bikaneri Bhujia 200g",80,0.2),
("Snacks","Namkeen","Bikaji Navratan Mix 200g",80,0.2),
("Snacks","Namkeen","Haldirams Peanuts 200g",70,0.2),
("Snacks","Namkeen","Haldirams Moong Dal 200g",75,0.2),
("Snacks","Namkeen","Bikaji Khatta Meetha 200g",80,0.2),
("Snacks","Namkeen","Haldirams Chana Chur 200g",75,0.2),
("Snacks","Namkeen","Haldirams All In One 400g",150,0.4),
("Snacks","Namkeen","Bikaji Bikaneri Mix 400g",140,0.4),

# ── SNACKS: BISCUITS ─────────────────────────────────────────────────────────
("Snacks","Biscuits","Parle-G Glucose Biscuits 250g",15,0.25),
("Snacks","Biscuits","Parle-G Glucose Biscuits 800g",40,0.8),
("Snacks","Biscuits","Britannia Good Day Cashew 200g",55,0.2),
("Snacks","Biscuits","Britannia NutriChoice 5 Grain 150g",60,0.15),
("Snacks","Biscuits","Britannia Bourbon Cream 200g",45,0.2),
("Snacks","Biscuits","Britannia Marie Gold 250g",30,0.25),
("Snacks","Biscuits","Britannia 50-50 Sweet Salty 195g",40,0.195),
("Snacks","Biscuits","Sunfeast Dark Fantasy Choco Fills 75g",30,0.075),
("Snacks","Biscuits","Sunfeast Moms Magic Butter Sugar 200g",40,0.2),
("Snacks","Biscuits","Oreo Chocolate Sandwich 120g",40,0.12),
("Snacks","Biscuits","Oreo Vanilla Sandwich 120g",40,0.12),
("Snacks","Biscuits","Parle Hide Seek Chocolate 100g",35,0.1),
("Snacks","Biscuits","Unibic Choco Chip Cookies 150g",55,0.15),
("Snacks","Biscuits","Mcvities Digestive Original 250g",95,0.25),
("Snacks","Biscuits","Lotus Biscoff Cookies 250g",195,0.25),
("Snacks","Biscuits","Krackjack Sweet Salty 200g",35,0.2),
("Snacks","Biscuits","Good Day Butter 200g",50,0.2),
("Snacks","Biscuits","Parle Monaco Salted 200g",30,0.2),

# ── SNACKS: NUTS & DRY FRUITS ────────────────────────────────────────────────
("Snacks","Nuts","Happilo 100% Natural Almonds 200g",260,0.2),
("Snacks","Nuts","Nutraj Cashews W320 200g",220,0.2),
("Snacks","Nuts","Tata Sampann Premium Cashews 200g",230,0.2),
("Snacks","Nuts","Nutraj Raisins 250g",120,0.25),
("Snacks","Nuts","Happilo Raisins Green 200g",110,0.2),
("Snacks","Nuts","Nutraj Walnuts Kernels 200g",380,0.2),
("Snacks","Nuts","Nutraj Pistachios Roasted 100g",200,0.1),
("Snacks","Nuts","Happilo Pistachios 200g",380,0.2),
("Snacks","Nuts","Wonderland Peanuts Roasted Salted 200g",55,0.2),
("Snacks","Nuts","Bikaji Peanuts Masala 200g",60,0.2),
("Snacks","Nuts","Tata Sampann Dry Dates 200g",130,0.2),
("Snacks","Nuts","Lion Dates 250g",80,0.25),
("Snacks","Nuts","Happilo Mixed Dry Fruits 250g",320,0.25),

# ── SNACKS: CHOCOLATES ───────────────────────────────────────────────────────
("Snacks","Chocolate","Dairy Milk Silk 60g",65,0.06),
("Snacks","Chocolate","Dairy Milk Crackle 40g",40,0.04),
("Snacks","Chocolate","KitKat 4 Finger 41.5g",40,0.0415),
("Snacks","Chocolate","5 Star 40g",20,0.04),
("Snacks","Chocolate","Munch 25g",10,0.025),
("Snacks","Chocolate","Dairy Milk Fruit Nut 100g",120,0.1),
("Snacks","Chocolate","Bournville Dark 80g",100,0.08),
("Snacks","Chocolate","Toblerone Swiss Milk 100g",280,0.1),
("Snacks","Chocolate","Ferrero Rocher 16 Pcs 200g",499,0.2),
("Snacks","Chocolate","Snickers 50g",40,0.05),
("Snacks","Chocolate","Twix 58g",45,0.058),
("Snacks","Chocolate","Bounty 57g",45,0.057),
("Snacks","Chocolate","M&M's Peanut 90g",80,0.09),

# ── SPICES & MASALAS ─────────────────────────────────────────────────────────
("Spices","Whole","Everest Cumin Seeds 100g",60,0.1),
("Spices","Whole","MDH Coriander Seeds 100g",35,0.1),
("Spices","Whole","Catch Mustard Seeds 100g",30,0.1),
("Spices","Whole","Everest Fennel Seeds 100g",65,0.1),
("Spices","Whole","Black Pepper Whole 50g",95,0.05),
("Spices","Whole","Cloves Whole 50g",120,0.05),
("Spices","Whole","Cardamom Green 50g",175,0.05),
("Spices","Whole","Cinnamon Sticks 50g",60,0.05),
("Spices","Powder","Everest Turmeric Powder 200g",55,0.2),
("Spices","Powder","MDH Turmeric Powder 500g",120,0.5),
("Spices","Powder","Catch Red Chilli Powder 200g",65,0.2),
("Spices","Powder","Everest Red Chilli Powder 200g",70,0.2),
("Spices","Powder","Catch Coriander Powder 200g",55,0.2),
("Spices","Powder","Everest Garam Masala 100g",95,0.1),
("Spices","Powder","MDH Chana Masala 100g",80,0.1),
("Spices","Masala","MDH Kitchen King Masala 100g",90,0.1),
("Spices","Masala","Everest Rajma Masala 100g",80,0.1),
("Spices","Masala","Catch Biryani Masala 50g",65,0.05),
("Spices","Masala","MDH Biryani Masala 50g",75,0.05),
("Spices","Masala","Everest Chicken Masala 100g",95,0.1),
("Spices","Masala","MDH Mutton Masala 50g",80,0.05),
("Spices","Masala","Patanjali Haldi Powder 200g",45,0.2),
("Spices","Powder","MDH Sambar Masala 200g",115,0.2),
("Spices","Masala","Everest Sabzi Masala 100g",80,0.1),
("Spices","Salt","Tata Salt 1kg",25,1.0),
("Spices","Salt","Annapurna Salt 1kg",26,1.0),
("Spices","Salt","Saffola Fittify Pink Himalayan Salt 200g",70,0.2),

# ── CONDIMENTS & SAUCES ──────────────────────────────────────────────────────
("Condiments","Sauce","Kissan Tomato Ketchup 500g",90,0.5),
("Condiments","Sauce","Kissan Tomato Ketchup 1kg",160,1.0),
("Condiments","Sauce","Heinz Tomato Ketchup 450g",175,0.45),
("Condiments","Sauce","Maggi Hot Sweet Sauce 500g",120,0.5),
("Condiments","Sauce","Maggi Tamarind Sauce 500g",115,0.5),
("Condiments","Sauce","Ching's Red Chilli Sauce 200g",55,0.2),
("Condiments","Sauce","Lee Kum Kee Soy Sauce 150ml",75,0.15),
("Condiments","Sauce","Kikkoman Soy Sauce 150ml",145,0.15),
("Condiments","Mayonnaise","Dr Oetker Funfoods Veg Mayo 250g",90,0.25),
("Condiments","Mayonnaise","Hellmanns Real Mayonnaise 315g",270,0.315),
("Condiments","Mayonnaise","Veeba Burger Mayo 300g",120,0.3),
("Condiments","Pickle","Patanjali Mango Pickle 500g",80,0.5),
("Condiments","Pickle","Priya Avakaya Mango Pickle 300g",95,0.3),
("Condiments","Pickle","Bedekar Mixed Pickle 400g",110,0.4),
("Condiments","Jam","Kissan Mixed Fruit Jam 500g",130,0.5),
("Condiments","Jam","Smucker Strawberry Preserve 340g",295,0.34),
("Condiments","Spread","Sundrop Peanut Butter Creamy 462g",260,0.462),
("Condiments","Spread","Dr Oetker Peanut Butter Crunchy 350g",240,0.35),
("Condiments","Spread","Nutella 350g",465,0.35),
("Condiments","Honey","Dabur Honey 500g",215,0.5),
("Condiments","Honey","Patanjali Natural Honey 500g",200,0.5),
("Condiments","Vinegar","Borges Red Wine Vinegar 500ml",155,0.5),
("Condiments","Sugar","Uttam Sugar 1kg",50,1.0),
("Condiments","Sugar","Patanjali Organic Sugar 1kg",65,1.0),
("Condiments","Sugar","Dhampure Specialty Sugars 500g",95,0.5),

# ── BREAKFAST & CEREAL ───────────────────────────────────────────────────────
("Breakfast","Cereal","Kelloggs Corn Flakes 875g",390,0.875),
("Breakfast","Cereal","Kelloggs Chocos Chocolate 700g",280,0.7),
("Breakfast","Cereal","Kelloggs Muesli Fruit 750g",350,0.75),
("Breakfast","Oats","Quaker Oats Rolled 500g",130,0.5),
("Breakfast","Oats","Quaker Oats 1kg",220,1.0),
("Breakfast","Oats","Saffola Oats 1kg",180,1.0),
("Breakfast","Oats","True Elements Rolled Oats 1kg",240,1.0),
("Breakfast","Cereal","Kelloggs Special K 440g",320,0.44),
("Breakfast","Health Drink","Nestle Milo 400g",350,0.4),
("Breakfast","Health Drink","Bournvita Chocolate Drink 500g",275,0.5),
("Breakfast","Health Drink","Horlicks Original 500g",260,0.5),
("Breakfast","Health Drink","Complan Chocolate 500g",305,0.5),

# ── BAKERY ───────────────────────────────────────────────────────────────────
("Bakery","Bread","Britannia 100% Whole Wheat Bread 400g",45,0.4),
("Bakery","Bread","Modern Brown Bread 400g",42,0.4),
("Bakery","Bread","English Oven White Sandwich Bread 400g",40,0.4),
("Bakery","Bread","Harvest Gold White Bread 400g",38,0.4),
("Bakery","Bread","Britannia Multigrain Bread 400g",52,0.4),
("Bakery","Bread","Bonn Multigrain Bread 400g",50,0.4),
("Bakery","Buns","English Oven Burger Buns 6pcs 240g",55,0.24),
("Bakery","Buns","Harvest Gold Pavbhaji Pav 200g",35,0.2),
("Bakery","Cakes","Britannia Chocolate Cake 60g",25,0.06),
("Bakery","Cakes","Britannia Fruit Cake 400g",130,0.4),
("Bakery","Rusk","Britannia Toast 200g",50,0.2),
("Bakery","Rusk","Modern Rusk 180g",45,0.18),

# ── CANNED & PACKAGED ────────────────────────────────────────────────────────
("Packaged","Canned Veg","Del Monte Sweet Corn 420g",85,0.42),
("Packaged","Canned Veg","Green Giant Whole Kernel Corn 198g",75,0.198),
("Packaged","Canned Veg","Del Monte Baked Beans 450g",95,0.45),
("Packaged","Canned Fruit","Del Monte Pineapple Slices 820g",145,0.82),
("Packaged","Canned Fish","Catch Tuna in Brine 185g",130,0.185),
("Packaged","Soup","Knorr Tomato Soup Mix 75g",55,0.075),
("Packaged","Soup","Campbell Tomato Soup 300ml",85,0.3),
("Packaged","Soup","Maggi Masala Soup 55g",35,0.055),

# ── FROZEN FOODS ─────────────────────────────────────────────────────────────
("Frozen","Frozen Snacks","McCain Classic Smiles 415g",180,0.415),
("Frozen","Frozen Snacks","McCain Cheese Shots 375g",170,0.375),
("Frozen","Frozen Snacks","McCain French Fries 400g",130,0.4),
("Frozen","Frozen Veg","Safal Green Peas 500g",75,0.5),
("Frozen","Frozen Veg","Safal Mix Vegetables 500g",90,0.5),
("Frozen","Frozen Snacks","Godrej Yummiez Chicken Nuggets 250g",260,0.25),

# ── PERSONAL CARE: SOAP & BODY WASH ─────────────────────────────────────────
("Personal Care","Soap","Dove Beauty Cream Bar 100g",55,0.1),
("Personal Care","Soap","Lux Soft Touch 100g",40,0.1),
("Personal Care","Soap","Dettol Original Bar Soap 125g",60,0.125),
("Personal Care","Soap","Pears Transparent Soap 125g",65,0.125),
("Personal Care","Soap","Hamam Bar 150g",55,0.15),
("Personal Care","Soap","Lifebuoy Total 10 Soap 100g",35,0.1),
("Personal Care","Soap","Nivea Creme Soft Soap 75g",60,0.075),
("Personal Care","Body Wash","Dove Go Fresh Body Wash 500ml",330,0.5),
("Personal Care","Body Wash","Nivea Fresh Active Body Wash 500ml",290,0.5),
("Personal Care","Body Wash","Fiama Shower Gel 250ml",220,0.25),
("Personal Care","Body Wash","Himalaya Refreshing Body Wash 200ml",165,0.2),
("Personal Care","Body Lotion","Vaseline Intensive Care Aloe 400ml",220,0.4),
("Personal Care","Body Lotion","Parachute Soft Touch Body Lotion 400ml",195,0.4),

# ── PERSONAL CARE: SHAMPOO & CONDITIONER ────────────────────────────────────
("Personal Care","Shampoo","Dove Intense Repair Shampoo 340ml",340,0.34),
("Personal Care","Shampoo","Head Shoulders Anti Dandruff 340ml",310,0.34),
("Personal Care","Shampoo","Pantene Pro-V Silky Smooth Shampoo 340ml",320,0.34),
("Personal Care","Shampoo","TRESemme Keratin Smooth Shampoo 340ml",300,0.34),
("Personal Care","Shampoo","Clinic Plus Strength Shine Shampoo 340ml",140,0.34),
("Personal Care","Shampoo","Sunsilk Smooth Shine Shampoo 340ml",160,0.34),
("Personal Care","Shampoo","Biotique Bio Kelp Shampoo 200ml",265,0.2),
("Personal Care","Shampoo","Himalaya Damage Repair Shampoo 200ml",175,0.2),
("Personal Care","Conditioner","Dove Intense Repair Conditioner 180ml",220,0.18),
("Personal Care","Conditioner","TRESemme Smooth Shine Conditioner 190ml",210,0.19),
("Personal Care","Conditioner","Pantene Pro-V Daily Moisture Conditioner 180ml",240,0.18),

# ── PERSONAL CARE: HAIR OIL ──────────────────────────────────────────────────
("Personal Care","Hair Oil","Parachute Coconut Oil 200ml",100,0.2),
("Personal Care","Hair Oil","Parachute Coconut Oil 500ml",210,0.5),
("Personal Care","Hair Oil","Bajaj Almond Drops Hair Oil 200ml",165,0.2),
("Personal Care","Hair Oil","Dabur Amla Hair Oil 300ml",140,0.3),
("Personal Care","Hair Oil","Kesh King Scalp Hair Oil 300ml",235,0.3),
("Personal Care","Hair Oil","Patanjali Kesh Kanti Oil 200ml",90,0.2),
("Personal Care","Hair Oil","WOW Onion Black Seed Hair Oil 200ml",349,0.2),

# ── PERSONAL CARE: SKIN CARE ─────────────────────────────────────────────────
("Personal Care","Skin Care","Nivea Soft Moisturising Cream 200ml",225,0.2),
("Personal Care","Skin Care","Ponds Light Moisturiser 147ml",175,0.147),
("Personal Care","Skin Care","Cetaphil Moisturising Lotion 250ml",445,0.25),
("Personal Care","Skin Care","Himalaya Aloe Vera Gel 300ml",130,0.3),
("Personal Care","Skin Care","Lakme Peach Milk Moisturiser SPF 24 120ml",225,0.12),
("Personal Care","Sunscreen","Neutrogena Ultra Sheer SPF 50 88ml",520,0.088),
("Personal Care","Sunscreen","Lotus Herbals Safe Sun UV Screen SPF 50 50g",260,0.05),
("Personal Care","Sunscreen","Lakme Sun Expert SPF 50 100ml",310,0.1),
("Personal Care","Face Wash","Cetaphil Gentle Skin Cleanser 250ml",510,0.25),
("Personal Care","Face Wash","Garnier Bright Complete Face Wash 100g",150,0.1),
("Personal Care","Face Wash","Himalaya Purifying Neem Face Wash 200ml",165,0.2),

# ── PERSONAL CARE: ORAL CARE ─────────────────────────────────────────────────
("Personal Care","Oral Care","Colgate MaxFresh Toothpaste 150g",95,0.15),
("Personal Care","Oral Care","Sensodyne Fresh Mint Toothpaste 80g",185,0.08),
("Personal Care","Oral Care","Pepsodent Germicheck Toothpaste 150g",80,0.15),
("Personal Care","Oral Care","Himalaya Complete Care Toothpaste 150g",120,0.15),
("Personal Care","Oral Care","Patanjali Dant Kanti 200g",60,0.2),
("Personal Care","Oral Care","Oral-B Pro-Health Toothbrush Medium",75,0.025),
("Personal Care","Oral Care","Colgate Extra Clean Toothbrush Medium",60,0.025),
("Personal Care","Oral Care","Listerine Cool Mint Mouthwash 250ml",175,0.25),
("Personal Care","Oral Care","Oral-B Mouthwash Healthy White 250ml",190,0.25),

# ── PERSONAL CARE: DEODORANT ─────────────────────────────────────────────────
("Personal Care","Deodorant","Wild Stone Forest Spice Deo Spray 150ml",175,0.15),
("Personal Care","Deodorant","Fogg Fresh Woody Deo Spray 150ml",215,0.15),
("Personal Care","Deodorant","Nivea Men Fresh Active Deo 150ml",195,0.15),
("Personal Care","Deodorant","Dove Original Deo Spray 150ml",225,0.15),
("Personal Care","Deodorant","Axe Dark Temptation Deo Spray 150ml",205,0.15),
("Personal Care","Deodorant","Set Wet Swagger Deo Spray 150ml",140,0.15),

# ── PERSONAL CARE: FEMININE HYGIENE ─────────────────────────────────────────
("Personal Care","Feminine Hygiene","Whisper Ultra Clean 30 Pads",245,0.13),
("Personal Care","Feminine Hygiene","Stayfree Secure Cottony 20 Pads",195,0.1),
("Personal Care","Feminine Hygiene","Sofy Bodyfit Night 15 Pads",255,0.13),

# ── BABY CARE ────────────────────────────────────────────────────────────────
("Baby Care","Diapers","Pampers Active Baby Dry M 34 Pcs",699,0.85),
("Baby Care","Diapers","Huggies Wonder Pants M 30 Pcs",699,0.82),
("Baby Care","Baby Skin","Johnson's Baby Lotion 200ml",185,0.2),
("Baby Care","Baby Skin","Johnson's Baby Shampoo 200ml",165,0.2),
("Baby Care","Baby Skin","Himalaya Baby Cream 200g",210,0.2),
("Baby Care","Baby Food","Cerelac Stage 1 Wheat 300g",250,0.3),
("Baby Care","Baby Food","Nestle NanPro 1 Infant Formula 400g",575,0.4),
("Baby Care","Baby Wipes","Johnson's Baby Wipes 80pcs",230,0.24),

# ── HOUSEHOLD: LAUNDRY ───────────────────────────────────────────────────────
("Household","Laundry","Surf Excel Matic Liquid 1L",380,1.0),
("Household","Laundry","Ariel Matic Front Load Powder 1kg",305,1.0),
("Household","Laundry","Tide Plus Detergent Powder 2kg",290,2.0),
("Household","Laundry","Henko Stain Champion Powder 1kg",160,1.0),
("Household","Laundry","Wheel Active Detergent 1kg",80,1.0),
("Household","Laundry","Comfort Morning Fresh Fabric Conditioner 800ml",285,0.8),
("Household","Dishwash","Pril Dishwash Liquid 750ml",135,0.75),
("Household","Dishwash","Vim Dishwash Liquid 750ml",130,0.75),
("Household","Dishwash","Exo Dishwash Bar 500g",50,0.5),
("Household","Dishwash","Surf Excel Dishwash Bar 500g",55,0.5),

# ── HOUSEHOLD: CLEANING ──────────────────────────────────────────────────────
("Household","Cleaning","Harpic Power Plus 1L",165,1.0),
("Household","Cleaning","Lizol Floor Cleaner Floral 1L",199,1.0),
("Household","Cleaning","Colin Glass Surface Cleaner 500ml",150,0.5),
("Household","Cleaning","Domex Multi-Purpose Bleach 1L",135,1.0),
("Household","Cleaning","Dettol Multi-Use Hygiene Liquid 500ml",195,0.5),
("Household","Cleaning","Scotch Brite Scrub Sponge 3 Pcs",79,0.09),
("Household","Cleaning","Mr Muscle Advanced Power 5in1 500ml",185,0.5),

# ── HOUSEHOLD: PAPER & DISPOSABLES ──────────────────────────────────────────
("Household","Paper","Paseo Toilet Tissue 10 Rolls",245,1.1),
("Household","Paper","Scotts Toilet Tissue 12 Rolls",280,1.3),
("Household","Paper","Kleenex Facial Tissues 200 Sheets",155,0.2),
("Household","Disposables","Safal Cling Wrap 100m",130,0.15),
("Household","Disposables","Ezee Aluminium Foil 9m x 30cm",80,0.14),
("Household","Disposables","Glean Garbage Bags 30 Pcs",75,0.15),

# ── HEALTH & WELLNESS ─────────────────────────────────────────────────────────
("Health","Vitamins","HealthViva Vitamin C 500mg 60 tablets",275,0.07),
("Health","Vitamins","MuscleBlaze Vitamin D3 60 capsules",420,0.06),
("Health","Protein","MuscleBlaze Whey Active 1kg",1599,1.0),
("Health","Ayurveda","Dabur Chyawanprash 500g",255,0.5),
("Health","Ayurveda","Patanjali Ashwagandha 60 Tablets",120,0.06),
("Health","Digestive","Eno Fruit Salt Regular 30g",55,0.03),
("Health","Digestive","Pudin Hara Liquid 25ml",85,0.025),
("Health","Immunity","Dabur Giloy Juice 1L",185,1.0),
("Health","Immunity","Patanjali Amla Aloevera Juice 1L",120,1.0),
]

# Smart size variants: These are realistic alternate sizes for each product category
SOLID_VARIANTS = {
    "Atta":         [("2kg", 2.0, 0.45), ("5kg", 5.0, 0.85), ("10kg", 10.0, 1.65)],
    "Flour":        [("500g", 0.5, 0.55), ("1kg", 1.0, 1.0), ("2kg", 2.0, 1.8)],
    "Rice":         [("1kg", 1.0, 0.23), ("5kg", 5.0, 1.0)],
    "Dal":          [("500g", 0.5, 0.55), ("2kg", 2.0, 1.8)],
    "Beans":        [("1kg", 1.0, 1.8)],
    "Oats":         [("1kg", 1.0, 1.85)],
    "Biscuits":     [("400g", 0.4, 1.8)],
    "Namkeen":      [("100g", 0.1, 0.6), ("400g", 0.4, 1.7)],
    "Spices":       [("50g", 0.05, 0.55), ("200g", 0.2, 1.8)],
    "Chocolate":    [("200g", 0.2, 3.0)],
    "Cereal":       [("500g", 0.5, 0.6)],
}
LIQUID_VARIANTS = {
    "Cooking Oil":  [("500ml", 0.46, 0.55), ("2L", 1.84, 1.8)],
    "Body Wash":    [("100ml", 0.1, 0.45)],
    "Shampoo":      [("100ml", 0.1, 0.4)],
    "Juice":        [("200ml", 0.2, 0.3)],
    "Soda":         [("2L", 2.0, 2.5)],
}


def extend_to_1000(prods):
    """Add realistic size variants until we reach 1000."""
    existing = {p[2] for p in prods}
    extended = list(prods)

    # Merge variant tables
    variant_map = {**SOLID_VARIANTS, **LIQUID_VARIANTS}

    idx = 0
    while len(extended) < 1000:
        cat, sub, name, price, wt = prods[idx % len(prods)]

        if sub in variant_map:
            for suffix, new_wt, factor in variant_map[sub]:
                # Strip last word (old size) and replace
                base_name = name.rsplit(' ', 1)[0]
                candidate = f"{base_name} {suffix}"
                if candidate not in existing and candidate != name:
                    existing.add(candidate)
                    extended.append((cat, sub, candidate, round(price * factor), new_wt))
                    if len(extended) >= 1000:
                        break
        idx += 1
        if idx > len(prods) * 20:  # safety stop
            break

    return extended


def main():
    import random
    random.seed(42)  # deterministic so each run is reproducible

    print("Generating unique products CSV...")
    prods = PRODUCTS
    total = len(prods)
    print(f"  Product definitions loaded: {total}")

    if total < 1000:
        print(f"  Extending to 1000 with realistic variants...")
        prods = extend_to_1000(prods)

    prods = prods[:1000]
    print(f"  Final product count: {len(prods)}")

    # Stock distribution to realistically trigger low-stock & restock alerts:
    #   ~15% critically low  (1–5)  → below reorder level, triggers alert
    #   ~20% low             (6–15) → near reorder level
    #   ~40% medium          (20–50)→ healthy stock
    #   ~25% well-stocked    (60–150)→ surplus
    def pick_stock(i):
        roll = random.random()
        if roll < 0.15:
            return random.randint(1, 5)      # critical
        elif roll < 0.35:
            return random.randint(6, 15)     # low
        elif roll < 0.75:
            return random.randint(20, 50)    # medium
        else:
            return random.randint(60, 150)   # well-stocked

    rows = []
    for i, (cat, sub, name, price, wt) in enumerate(prods, start=1):
        prod_id  = f"PROD{i:05d}"
        barcode  = f"89010{i:05d}"
        stock    = pick_stock(i)
        reorder  = 8   # reorder level: stock <= 8 triggers low-stock alerts
        rows.append({
            "Product_ID":     prod_id,
            "Barcode":        barcode,
            "Product_Name":   name,
            "Price":          price,
            "Weight_kg":      wt,
            "Category":       cat,
            "Sub_Category":   sub,
            "Aisle_No":       0,
            "Partition_No":   0,
            "Shelf_No":       "0.0",
            "Position_Tag":   "P000",
            "Side":           "Left",
            "Stock_Quantity": stock,
            "Reorder_Level":  reorder,
        })

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)

    low  = sum(1 for r in rows if r["Stock_Quantity"] <= r["Reorder_Level"])
    print(f"  Written {len(rows)} products to {OUT_CSV}")
    print(f"  Stock summary: {low} products at or below reorder level ({low/len(rows)*100:.1f}%)")
    print("  → Now run: python remap_layout.py")
    print("  → Then:    python import_to_neon.py")
    print("  → Then:    python import_products2.py")


if __name__ == "__main__":
    main()

