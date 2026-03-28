#!/usr/bin/env python3
"""
add_products2_top500.py
Clears products2 and inserts exactly 500 new real-world Indian supermarket
products (distinct from the 500 in products table) with proper units,
realistic pricing, and varied stock levels.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os, random
from pathlib import Path
import psycopg2, psycopg2.extras

NEON_DSN = os.getenv(
    "NEON_DB_DSN",
    "postgresql://neondb_owner:npg_CWwZngUY50OJ@ep-curly-mud-adze9nhv-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)

random.seed(77)

# (Category, Sub_Category, Name, Price_INR, Weight_kg_internal)
# Liquids: weight_kg is actual mass (density ~1), unit in name is ml/L
PRODUCTS2 = [
# ── FRESH PRODUCE ────────────────────────────────────────────────────────────
("Fresh Produce","Vegetables","Baby Spinach 250g",45,0.25),
("Fresh Produce","Vegetables","Broccoli 500g",80,0.5),
("Fresh Produce","Vegetables","Cherry Tomatoes 250g",60,0.25),
("Fresh Produce","Vegetables","Button Mushrooms 200g",75,0.2),
("Fresh Produce","Vegetables","Sweet Corn 2 Pcs",35,0.35),
("Fresh Produce","Vegetables","Capsicum Red 500g",70,0.5),
("Fresh Produce","Vegetables","Capsicum Yellow 500g",70,0.5),
("Fresh Produce","Vegetables","Zucchini 500g",65,0.5),
("Fresh Produce","Vegetables","Spring Onion 100g",20,0.1),
("Fresh Produce","Vegetables","Bitter Gourd 500g",40,0.5),
("Fresh Produce","Vegetables","Drumstick 500g",35,0.5),
("Fresh Produce","Vegetables","Raw Banana 500g",30,0.5),
("Fresh Produce","Fruits","Strawberry 200g",80,0.2),
("Fresh Produce","Fruits","Kiwi 4 Pcs 400g",120,0.4),
("Fresh Produce","Fruits","Blueberry 125g",150,0.125),
("Fresh Produce","Fruits","Avocado 2 Pcs 400g",200,0.4),
("Fresh Produce","Fruits","Dragon Fruit 300g",160,0.3),
("Fresh Produce","Fruits","Pomegranate 500g",90,0.5),
("Fresh Produce","Fruits","Mango Alphonso 1kg",250,1.0),
("Fresh Produce","Fruits","Watermelon 1 Pcs 2kg",80,2.0),
("Fresh Produce","Herbs","Fresh Coriander 100g",15,0.1),
("Fresh Produce","Herbs","Fresh Mint 100g",20,0.1),
("Fresh Produce","Herbs","Curry Leaves 50g",10,0.05),
("Fresh Produce","Herbs","Fresh Ginger 200g",30,0.2),
("Fresh Produce","Herbs","Garlic 250g",50,0.25),

# ── MEAT & SEAFOOD ────────────────────────────────────────────────────────────
("Meat & Seafood","Chicken","Fresho Chicken Breast 500g",195,0.5),
("Meat & Seafood","Chicken","Suguna Fresh Chicken Curry Cut 1kg",280,1.0),
("Meat & Seafood","Chicken","Godrej Real Good Chicken Wings 500g",175,0.5),
("Meat & Seafood","Chicken","Venky's Chicken Sausages 400g",215,0.4),
("Meat & Seafood","Egg","Pran NE Omega3 Eggs 6 Pcs",75,0.36),
("Meat & Seafood","Egg","Country Eggs 12 Pcs",105,0.72),
("Meat & Seafood","Egg","Keggfarms White Eggs 6 Pcs",65,0.36),
("Meat & Seafood","Fish","Fresh Rohu Fillet 500g",240,0.5),
("Meat & Seafood","Fish","Prawns Medium 500g",380,0.5),
("Meat & Seafood","Fish","Catla Fish Fillet 500g",220,0.5),

# ── INDIAN READY MEALS ────────────────────────────────────────────────────────
("Ready Meals","Indian","MTR Dal Makhani 300g",90,0.3),
("Ready Meals","Indian","MTR Palak Paneer 300g",100,0.3),
("Ready Meals","Indian","Haldirams Pav Bhaji 300g",85,0.3),
("Ready Meals","Indian","ITC Kitchens of India Butter Chicken 285g",130,0.285),
("Ready Meals","Indian","Gits Dosa Mix 500g",95,0.5),
("Ready Meals","Indian","MTR Upma Mix 200g",65,0.2),
("Ready Meals","Indian","Gits Gulab Jamun Mix 200g",90,0.2),
("Ready Meals","Indian","Haldirams Kheer Mix 200g",85,0.2),
("Ready Meals","Indian","MTR Pulao Masala 50g",35,0.05),
("Ready Meals","Snack Mixes","Knorr Chinese Noodles 70g",30,0.07),
("Ready Meals","Snack Mixes","Ching's Schezwan Chutney 250g",80,0.25),

# ── PICKLES & CHUTNEYS ────────────────────────────────────────────────────────
("Condiments","Chutney","Ferns N Petals Green Chutney 200g",70,0.2),
("Condiments","Chutney","Druk Tamarind Chutney 200g",60,0.2),
("Condiments","Chutney","Priya Gongura Chutney 300g",80,0.3),
("Condiments","Chutney","MTR Coconut Chutney Powder 100g",55,0.1),
("Condiments","Pickle","Mothers Recipe Lime Pickle 400g",120,0.4),
("Condiments","Pickle","Priya Garlic Pickle 300g",90,0.3),
("Condiments","Pickle","Aachi Mango Pickle 400g",85,0.4),
("Condiments","Dressing","Veeba Honey Mustard Dressing 300g",130,0.3),
("Condiments","Dressing","Kraft Ranch Dressing 250ml",150,0.25),

# ── DAIRY ADDITIONAL ─────────────────────────────────────────────────────────
("Dairy","Flavoured Milk","Amul Kool Chocolate Milk 200ml",25,0.2),
("Dairy","Flavoured Milk","Amul Kool Kesar 200ml",25,0.2),
("Dairy","Flavoured Milk","Mother Dairy Lassi 200ml",25,0.2),
("Dairy","Flavoured Milk","Nandini Masala Butter Milk 200ml",20,0.2),
("Dairy","Flavoured Milk","Amul Masti Spiced Buttermilk 200ml",22,0.2),
("Dairy","Ice Cream","Amul Kool Falooda 200ml",30,0.2),
("Dairy","Ice Cream","Kwality Walls Feast Choco Bar 60ml",35,0.06),
("Dairy","Ice Cream","Naturals Ice Cream Mango 500ml",220,0.5),
("Dairy","Curd","Epigamia Mango Greek Yogurt 90g",55,0.09),
("Dairy","Curd","Nestle a+ Mishti Dahi 90g",30,0.09),

# ── BEVERAGES: HOT DRINKS ────────────────────────────────────────────────────
("Beverages","Cocoa","Cadbury Drinking Chocolate 200g",175,0.2),
("Beverages","Cocoa","Milo Energy Drink 400g",350,0.4),
("Beverages","Malted","Boost Energy Food Drink 500g",295,0.5),
("Beverages","Malted","Protinex Vanilla 250g",490,0.25),
("Beverages","Malted","Pediasure Vanilla 400g",620,0.4),

# ── BEVERAGES: COLD ──────────────────────────────────────────────────────────
("Beverages","Flavoured Water","Appy Fizz 250ml",20,0.25),
("Beverages","Flavoured Water","Limca Nimbu Zero 300ml",20,0.3),
("Beverages","Herbal Drink","Dabur Sharbat Rooh Afza 750ml",215,0.75),
("Beverages","Herbal Drink","Baidyanath Amla Juice 500ml",90,0.5),
("Beverages","Herbal Drink","Patanjali Aloe Vera Juice 1L",120,1.0),
("Beverages","Sports","Gatorade Lime 500ml",80,0.5),
("Beverages","Sports","Powerade Mountain Berry 500ml",75,0.5),
("Beverages","Coconut Water","Raw Coconut Water 200ml",35,0.2),
("Beverages","Coconut Water","Tender Coconut 500ml",60,0.5),
("Beverages","Protein Shake","Ensure Vanilla 400g",700,0.4),

# ── SNACKS: POPCORN & OTHER ──────────────────────────────────────────────────
("Snacks","Popcorn","Orville Redenbacher Microwave Popcorn 290g",180,0.29),
("Snacks","Popcorn","Act II Butter Popcorn 33g",15,0.033),
("Snacks","Popcorn","YumFill Caramel Popcorn 100g",65,0.1),
("Snacks","Popcorn","Jimmy's Cocktail Popcorn 125g",80,0.125),
("Snacks","Crackers","Ritz Original Crackers 200g",120,0.2),
("Snacks","Crackers","Tuc Lite Crackers 130g",60,0.13),
("Snacks","Crackers","Digestive High Fibre 250g",100,0.25),
("Snacks","Candy","Mentos Original 40g",10,0.04),
("Snacks","Candy","Polo Mint 25g",5,0.025),
("Snacks","Candy","Alpenliebe Caramel 115g",50,0.115),
("Snacks","Candy","Center Fresh Spearmint Gum 65g",30,0.065),
("Snacks","Candy","Boomer Strawberry Gum 25g",10,0.025),
("Snacks","Energy Bar","Kind Almond Dark Chocolate Bar 40g",120,0.04),
("Snacks","Energy Bar","RiteBite Max Protein Bar 70g",100,0.07),
("Snacks","Energy Bar","Yoga Bar Oats Choco Chip 38g",55,0.038),
("Snacks","Energy Bar","Munch Nuts Peanut Bar 30g",20,0.03),
("Snacks","Sweets","Haldirams Motichoor Ladoo 500g",250,0.5),
("Snacks","Sweets","Haldirams Kaju Katli 250g",280,0.25),
("Snacks","Sweets","Bikaji Gujiya 500g",240,0.5),
("Snacks","Sweets","Balaji Sev 325g",85,0.325),

# ── BREAKFAST ADDITIONAL ─────────────────────────────────────────────────────
("Breakfast","Granola","Kelloggs Granola Almond Honey 460g",380,0.46),
("Breakfast","Granola","True Elements Muesli 500g",225,0.5),
("Breakfast","Pancake Mix","Pilsbury Pancake Mix 200g",120,0.2),
("Breakfast","Pancake Mix","Wingreens Waffle Mix 200g",140,0.2),
("Breakfast","Spreads","Borges Almond Butter 340g",480,0.34),
("Breakfast","Spreads","MyFitness Peanut Butter Chocolate 510g",420,0.51),
("Breakfast","Spreads","Mango Jam Mapro 200g",75,0.2),
("Breakfast","Cereals","Kelloggs Froot Loops 285g",240,0.285),
("Breakfast","Cereals","Kashi Go Crunch Honey Almond 400g",320,0.4),

# ── BAKERY ADDITIONAL ─────────────────────────────────────────────────────────
("Bakery","Cookies","Unibic Oatmeal Raisin Cookies 150g",80,0.15),
("Bakery","Cookies","McVities Digestive Dark Chocolate Biscuit 300g",145,0.3),
("Bakery","Cookies","Britannia GoodDay Pista Almond 200g",55,0.2),
("Bakery","Crackers","Parle Krackjack Creamy Onion 100g",25,0.1),
("Bakery","Pastry","Britannia Cake Slices Chocolate 50g",20,0.05),
("Bakery","Pastry","English Oven Croissant Butter 50g",25,0.05),
("Bakery","Croissant","Bonne Maman Croissant 120g",75,0.12),
("Bakery","Bread","Harvest Gold Multigrain Bread 400g",48,0.4),
("Bakery","Bread","English Oven Brown Bread 400g",44,0.4),

# ── SPICES ADDITIONAL ────────────────────────────────────────────────────────
("Spices","Whole","Star Anise 25g",60,0.025),
("Spices","Whole","Fenugreek Seeds 100g",30,0.1),
("Spices","Whole","Dried Red Chillies 100g",55,0.1),
("Spices","Powder","Everest Kashmiri Red Chilli Powder 100g",85,0.1),
("Spices","Powder","MDH Pav Bhaji Masala 100g",85,0.1),
("Spices","Powder","Catch Chaat Masala 100g",55,0.1),
("Spices","Powder","Everest Shahi Paneer Masala 50g",60,0.05),
("Spices","Powder","Shan Nihari Masala 60g",70,0.06),
("Spices","Masala","Priya Curry Powder 200g",75,0.2),
("Spices","Masala","MTR Puliyogare Powder 100g",55,0.1),
("Spices","Masala","Aachi Kabab Mix 50g",35,0.05),
("Spices","Masala","MDH Dal Makhani Masala 100g",90,0.1),
("Spices","Salt","Rock Salt Sendha Namak 1kg",60,1.0),
("Spices","Salt","Black Salt Kala Namak 100g",20,0.1),
("Spices","Essence","Vanilla Essence 28ml",55,0.028),
("Spices","Essence","Rose Water 200ml",60,0.2),

# ── GRAINS ADDITIONAL ────────────────────────────────────────────────────────
("Grains","Atta","Multigrain Atta 2kg",220,2.0),
("Grains","Atta","Organic Whole Wheat Atta 1kg",95,1.0),
("Grains","Rice","Brown Rice 1kg",130,1.0),
("Grains","Rice","Red Rice 1kg",145,1.0),
("Grains","Rice","Matta Rice 1kg",100,1.0),
("Grains","Rice","Poha Thick Flattened Rice 500g",55,0.5),
("Grains","Rice","Puffed Rice Murmura 400g",40,0.4),
("Grains","Millets","Foxtail Millet 500g",70,0.5),
("Grains","Millets","Pearl Millet Bajra 500g",50,0.5),
("Grains","Millets","Finger Millet Ragi 500g",65,0.5),
("Grains","Millets","Sorghum Jowar 500g",55,0.5),
("Grains","Millets","Kodo Millet 500g",80,0.5),
("Grains","Semolina","Bombay Rava 500g",45,0.5),
("Grains","Noodles","Indomie Instant Noodles Chicken 75g",25,0.075),
("Grains","Noodles","Wai Wai Noodles 75g",15,0.075),

# ── PULSES ADDITIONAL ────────────────────────────────────────────────────────
("Pulses","Dal","Arhar Pigeon Pea 500g",90,0.5),
("Pulses","Dal","Kulthi Horse Gram 500g",65,0.5),
("Pulses","Beans","Moth Beans Matki 500g",70,0.5),
("Pulses","Beans","Lima Beans 500g",80,0.5),
("Pulses","Soya","Nutrela Soya Chunks 200g",55,0.2),
("Pulses","Soya","Nutrela Mini Soya Chunks 200g",55,0.2),

# ── OILS ADDITIONAL ──────────────────────────────────────────────────────────
("Oils","Cooking Oil","Sunpure Refined Sunflower Oil 1L",165,0.92),
("Oils","Cooking Oil","Gold Winner Palm Oil 1L",130,0.92),
("Oils","Cooking Oil","Engine Coconut Oil 500ml",120,0.46),
("Oils","Cooking Oil","Parachute 100% Coconut Oil 500ml",140,0.46),
("Oils","Specialty","Natureland Sesame Oil 250ml",180,0.25),
("Oils","Specialty","Disano Canola Oil 1L",350,0.92),
("Oils","Ghee","Kwality Desi Ghee 500ml",310,0.5),
("Oils","Ghee","Sri Sri Tattva Cow Ghee 500ml",380,0.5),
("Oils","Ghee","Ananda Cow Ghee 1L",690,1.0),

# ── CANNED & PACKAGED ────────────────────────────────────────────────────────
("Packaged","Sauce","Lee Kum Kee Oyster Sauce 255g",165,0.255),
("Packaged","Sauce","Ching's Schezwan Sauce 250g",80,0.25),
("Packaged","Sauce","Veeba Pizza Pasta Sauce 300g",120,0.3),
("Packaged","Sauce","Del Monte Arrabiata Pasta Sauce 400g",145,0.4),
("Packaged","Sauce","Ragu Alfredo Sauce 425g",320,0.425),
("Packaged","Canned Veg","Del Monte Diced Tomatoes 400g",90,0.4),
("Packaged","Canned Veg","Green Giant Mushroom 400g",110,0.4),
("Packaged","Canned Veg","Del Monte Mixed Vegetables 415g",95,0.415),
("Packaged","Canned Fruit","Del Monte Fruit Cocktail 850g",195,0.85),
("Packaged","Canned Fish","Tuna Chunks in Oil 185g",140,0.185),
("Packaged","Canned Fish","Sardines in Tomato Sauce 200g",80,0.2),
("Packaged","Soup","Knorr Chicken Noodle Soup Mix 50g",65,0.05),
("Packaged","Soup","Campbell Cream of Mushroom 300ml",95,0.3),
("Packaged","Soup","Maggi Vegetable Soup 55g",45,0.055),

# ── FROZEN ADDITIONAL ─────────────────────────────────────────────────────────
("Frozen","Frozen Snacks","McCain Aloo Tikki 400g",160,0.4),
("Frozen","Frozen Snacks","Godrej Yummiez Paneer Strips 250g",240,0.25),
("Frozen","Frozen Snacks","Haldirams Frozen Samosa 400g",180,0.4),
("Frozen","Frozen Veg","Safal Sweet Corn 500g",85,0.5),
("Frozen","Frozen Veg","iD Fresh Malabar Paratha 5 Pcs",90,0.35),
("Frozen","Frozen Veg","iD Fresh Wheat Paratha 5 Pcs",85,0.35),
("Frozen","Frozen Non Veg","Venky's Chicken Keema 500g",280,0.5),
("Frozen","Ice Cream","Amul Vanilla Drumstick 80ml",55,0.08),
("Frozen","Ice Cream","Kwality Walls Cornetto Choco 100ml",65,0.1),

# ── PERSONAL CARE: HAIRCARE ──────────────────────────────────────────────────
("Personal Care","Hair Care","Livon Hair Serum 100ml",185,0.1),
("Personal Care","Hair Care","TRESemme Keratin Smooth Serum 100ml",225,0.1),
("Personal Care","Hair Care","Indulekha Bringha Hair Oil 100ml",295,0.1),
("Personal Care","Hair Care","Mamaearth Argan Shampoo 250ml",275,0.25),
("Personal Care","Hair Care","Wow Apple Cider Vinegar Shampoo 300ml",349,0.3),
("Personal Care","Hair Care","Himalaya Protein Shampoo 400ml",215,0.4),
("Personal Care","Hair Colour","Garnier Color Naturals Shade 2 Dark Brown",175,0.1),
("Personal Care","Hair Colour","Godrej No1 Hair Dye Black 20ml",25,0.02),
("Personal Care","Hair Colour","L'Oreal Excellence Cream 4.0 Brown 172ml",580,0.172),

# ── PERSONAL CARE: SKIN CARE ADDITIONAL ──────────────────────────────────────
("Personal Care","Skin Care","Biotique Papaya Body Scrub 175g",195,0.175),
("Personal Care","Skin Care","The Body Shop Vitamin E Moisturiser 100ml",850,0.1),
("Personal Care","Skin Care","Himalaya Nourishing Skin Cream 200ml",155,0.2),
("Personal Care","Skin Care","Lotus Herbals White Glow Cream 80g",210,0.08),
("Personal Care","Skin Care","Garnier Light Complete Cream 45g",150,0.045),
("Personal Care","Skin Care","Ponds Age Miracle Cream 50g",350,0.05),
("Personal Care","Lip Care","Vaseline Lip Therapy Aloe 7g",75,0.007),
("Personal Care","Lip Care","Maybelline Baby Lips 4g",130,0.004),
("Personal Care","Eye Care","Himalaya Under Eye Cream 15ml",175,0.015),

# ── PERSONAL CARE: GROOMING ──────────────────────────────────────────────────
("Personal Care","Shaving","Gillette Mach3 Razor 2 Pcs",250,0.05),
("Personal Care","Shaving","Gillette Fusion Shaving Gel 200g",295,0.2),
("Personal Care","Shaving","Old Spice After Shave Lotion 100ml",175,0.1),
("Personal Care","Shaving","Dettol Shaving Cream 60g",80,0.06),
("Personal Care","Shaving","Veet Hair Removal Cream 25g",65,0.025),
("Personal Care","Perfume","Wild Stone Code Deo Body Spray 150ml",250,0.15),
("Personal Care","Perfume","Engage On Spritz Pocket Perfume 18ml",195,0.018),
("Personal Care","Perfume","Park Avenue Good Morning Deo 150ml",175,0.15),

# ── HEALTH & WELLNESS ADDITIONAL ─────────────────────────────────────────────
("Health","Vitamins","VHM Fish Omega 3 Capsules 60 Pcs",350,0.06),
("Health","Vitamins","Himalaya Liv 52 Tablet 100 Pcs",195,0.08),
("Health","Vitamins","Dabur Nature Care Isabgol 100g",85,0.1),
("Health","Vitamins","Fast&Up Charge Vitamin C 20 Tabs",195,0.1),
("Health","Vitamins","HealthViva Biotin 5000mcg 60 Tabs",350,0.06),
("Health","Ayurveda","Himalaya Shatavari Tablet 60 Pcs",220,0.06),
("Health","Ayurveda","Dabur Triphala Churna 120g",100,0.12),
("Health","Ayurveda","Baidyanath Shilajit Capsule 20 Pcs",250,0.025),
("Health","Ayurveda","Patanjali Swasari Kwath 400ml",180,0.4),
("Health","Fitness","Saffola Fittify Green Coffee 30 Sachets",390,0.12),
("Health","Fitness","Oziva Protein Women 500g",1199,0.5),
("Health","Fitness","Fast&Up Whey Protein 1kg",1799,1.0),
("Health","First Aid","Johnson Band Aid Flexible 30 Pcs",150,0.04),
("Health","First Aid","Dettol Antiseptic Liquid 250ml",145,0.25),
("Health","First Aid","Betadine Solution 30ml",85,0.03),

# ── BABY CARE ADDITIONAL ──────────────────────────────────────────────────────
("Baby Care","Baby Food","Mead Johnson Enfagrow AP3 400g",799,0.4),
("Baby Care","Baby Food","Farex Stage 1 Rice 300g",220,0.3),
("Baby Care","Baby Skin","Johnson's Baby Powder 200g",175,0.2),
("Baby Care","Baby Skin","Himalaya Baby Soap 75g",60,0.075),
("Baby Care","Baby Skin","Chicco Baby Lotion 250ml",380,0.25),
("Baby Care","Baby Gear","Pigeon Wide Neck PP Bottle 240ml",280,0.24),
("Baby Care","Baby Gear","Mee Mee Silicone Nipple Size 3 2 Pcs",150,0.025),

# ── HOUSEHOLD: KITCHEN───────────────────────────────────────────────────────
("Household","Kitchen","Comet Steel Wool Scrubber 3 Pcs",55,0.09),
("Household","Kitchen","Prestige Induction Cooktop IC01 1600W",2495,2.5),
("Household","Kitchen","Parchment Paper Baking Sheet 10m",110,0.15),
("Household","Kitchen","Hawkins Stainless Steel Tiffin 3 Tier",450,0.6),
("Household","Kitchen","Milton Flask 500ml",350,0.3),
("Household","Kitchen","Borosil Freezer Safe Container 500ml",195,0.25),
("Household","Storage","Cello Opalware Bowl Set 6 Pcs",550,1.2),
("Household","Storage","Tupperware Lunch Box 1000ml",480,0.25),

# ── HOUSEHOLD: CLEANING ADDITIONAL ───────────────────────────────────────────
("Household","Cleaning","Vim Dishwash Gel 900ml",160,0.9),
("Household","Cleaning","Pril Dishwash Gel 900ml",165,0.9),
("Household","Cleaning","Lizol Pine Floor Cleaner 1L",195,1.0),
("Household","Cleaning","Good Knight Gold Flash 45 ml",195,0.045),
("Household","Cleaning","HIT Cockroach Killer Spray 200ml",165,0.2),
("Household","Cleaning","Mortein Power Booster 250ml",175,0.25),
("Household","Cleaning","Fevi Stick Glue 8g",25,0.008),
("Household","Laundry","Rin Detergent Powder 1kg",100,1.0),
("Household","Laundry","Surf Excel Easy Wash Powder 1kg",115,1.0),
("Household","Laundry","Vanish Stain Remover Powder 400g",195,0.4),
("Household","Laundry","Ujala White Fabric Whitener 200ml",65,0.2),

# ── STATIONERY & SCHOOL ───────────────────────────────────────────────────────
("Stationery","Pens","Reynolds 045 Ball Pen Blue 10 Pack",60,0.06),
("Stationery","Pens","Pilot V7 Hi-Techpoint Blue",55,0.012),
("Stationery","Pencil","Nataraj Pencil HB 10 Pack",45,0.08),
("Stationery","Notebook","Classmate Notebook A4 200 Pages",80,0.35),
("Stationery","Notebook","Kokuyo Campus Notebook B5 80 Pages",90,0.2),
("Stationery","Art","Faber Castell Color Pencils 24 Pcs",180,0.25),
("Stationery","Art","Camel Water Color 12 Pcs",95,0.15),
("Stationery","Tape","Sellotape Clear 18mm x 33m",45,0.06),
("Stationery","Scissors","Faber Castell Safety Scissors",60,0.08),

# ── PET CARE ──────────────────────────────────────────────────────────────────
("Pet Care","Dog Food","Pedigree Adult Chicken Rice 1.2kg",350,1.2),
("Pet Care","Dog Food","Royal Canin Adult Maxi 3kg",1650,3.0),
("Pet Care","Cat Food","Whiskas Adult Ocean Fish 1.2kg",380,1.2),
("Pet Care","Cat Food","Meo Chicken Cat Food 500g",195,0.5),
("Pet Care","Pet Snacks","Drools Chicken Biscuits 500g",250,0.5),
("Pet Care","Pet Care","Virbac Pet Shampoo 200ml",220,0.2),

# ── GARDEN & OUTDOOR ──────────────────────────────────────────────────────────
("Garden","Plants","Ugaoo Compost Fertilizer 1kg",150,1.0),
("Garden","Plants","Krishi Jagran Vermicompost 2kg",120,2.0),
("Garden","Plants","Ugaoo Plant Mist Spray Bottle 500ml",95,0.15),

# ── BEVERAGES: HEALTH JUICES ────────────────────────────────────────────────
("Beverages","Health Juice","Sattva Amla Giloy Juice 1L",195,1.0),
("Beverages","Health Juice","Kapiva Aloe Vera Juice 1L",210,1.0),
("Beverages","Health Juice","Jiva Ayurveda Wheat Grass Juice 500ml",180,0.5),
("Beverages","Health Juice","Baidyanath Karela Juice 500ml",150,0.5),
("Beverages","Health Juice","Patanjali Neem Juice 500ml",80,0.5),

# ── SNACKS: POPAD & FRYUMS ────────────────────────────────────────────────────
("Snacks","Fryums","Lijjat Papad Urad 200g",55,0.2),
("Snacks","Fryums","Haldirams Chatpata Fryums 80g",20,0.08),
("Snacks","Fryums","Bikaji Fryums 60g",15,0.06),
("Snacks","Traditional","Fortune Rice Papad 200g",50,0.2),
("Snacks","Traditional","Jabsons Groundnut Chikki 100g",30,0.1),
("Snacks","Traditional","Rajdhani Mathri 400g",120,0.4),
("Snacks","Traditional","Deep Gathiya 200g",60,0.2),

# ── SUGAR & BAKING ────────────────────────────────────────────────────────────
("Baking","Sugar","Madhur Pure Sugar 1kg",58,1.0),
("Baking","Sugar","Natureland Organic Jaggery 500g",75,0.5),
("Baking","Sugar","24 Mantra Organic Coconut Sugar 250g",150,0.25),
("Baking","Cocoa","Cadbury Bournville Cocoa 200g",195,0.2),
("Baking","Cocoa","Hersheys Cocoa Powder 226g",250,0.226),
("Baking","Baking Mix","Betty Crocker Chocolate Brownie Mix 500g",280,0.5),
("Baking","Baking Mix","Dr Oetker Moist Chocolate Cake Mix 280g",210,0.28),
("Baking","Baking Mix","Weikfield Custard Powder Vanilla 100g",60,0.1),
("Baking","Baking Mix","Pillsbury White Cake Mix 500g",170,0.5),
("Baking","Yeast","Blue Bird Baking Powder 100g",55,0.1),
("Baking","Yeast","Gloripan Instant Dry Yeast 500g",210,0.5),

# ── PERSONAL CARE: MEN'S GROOMING ────────────────────────────────────────────
("Personal Care","Men's Care","Beardo Beard Oil 30ml",349,0.03),
("Personal Care","Men's Care","Ustraa Face Wash Oily Skin 200ml",275,0.2),
("Personal Care","Men's Care","The Man Company Charcoal Face Scrub 100g",395,0.1),
("Personal Care","Men's Care","Bombay Shaving Company Shave Cream 100g",299,0.1),

# ── PERSONAL CARE: WOMEN'S CARE ──────────────────────────────────────────────
("Personal Care","Women's Care","WOW Vitamin C Face Serum 30ml",395,0.03),
("Personal Care","Women's Care","Mamaearth Vitamin C Night Cream 50g",349,0.05),
("Personal Care","Women's Care","The Derma Co Hyaluronic Serum 30ml",499,0.03),
("Personal Care","Women's Care","Plum Bright Years Cell Renew Night Cream 50g",575,0.05),
("Personal Care","Women's Care","Nykaa Skin Secrets Face Mask Charcoal 25g",75,0.025),

# ── DENTAL & EYE CARE ─────────────────────────────────────────────────────────
("Personal Care","Eye Care","Bausch Lomb Renu Solution 360ml",480,0.36),
("Personal Care","Eye Care","Systane Ultra Eye Drops 10ml",280,0.01),
("Personal Care","Dental","Waterpik Whitening Flossers 30 Pcs",195,0.03),
("Personal Care","Dental","Signal Herbal Toothpaste 75ml",75,0.075),
("Personal Care","Dental","Dabur Meswak Toothpaste 200g",85,0.2),
("Personal Care","Dental","Amway Glister Whitening Toothpaste 150g",245,0.15),

# ── ELECTRONICS (Basic Consumables) ──────────────────────────────────────────
("Electronics","Batteries","Duracell AA Alkaline Batteries 4 Pcs",180,0.1),
("Electronics","Batteries","Energizer AAA Batteries 4 Pcs",160,0.07),
("Electronics","Batteries","Philips AA Batteries 6 Pcs",140,0.15),
("Electronics","Bulbs","Philips LED Bulb 9W",120,0.08),
("Electronics","Bulbs","Syska LED Bulb 12W",130,0.09),
("Electronics","Extension","Anchor 3 Pin Extension Board 4 Socket 1.5m",350,0.4),

# ── CLOTHING CARE ─────────────────────────────────────────────────────────────
("Household","Clothing Care","Genteel Liquid Detergent 500ml",90,0.5),
("Household","Clothing Care","Rexona Sport Stain Remover 500ml",140,0.5),
("Household","Clothing Care","Naphthalene Balls 300g",65,0.3),
("Household","Clothing Care","Godrej Aer Pocket Bathroom Freshener 10g",75,0.01),

# ── GIFTING & SEASONAL ────────────────────────────────────────────────────────
("Gifting","Gift Box","Cadbury Celebrations Assorted 130g",195,0.13),
("Gifting","Gift Box","Haldirams Gift Pack Assorted 400g",350,0.4),
("Gifting","Gift Box","Ferrero Rocher Gift Box 4 Pcs 50g",175,0.05),

# ── OILS: SPECIALTY ──────────────────────────────────────────────────────────
("Oils","Specialty","WD-40 Multi-Use 200ml",250,0.2),
("Oils","Specialty","Keo Karpin Almond Enriched Hair Oil 300ml",145,0.3),
("Oils","Specialty","Vasmol 33 Kesh Kala Hair Oil 300ml",110,0.3),

# ── HOUSEHOLD: PEST CONTROL ───────────────────────────────────────────────────
("Household","Pest Control","Baygon Spray Cockroach Mosquito 400ml",225,0.4),
("Household","Pest Control","Good Knight Activ+ Refill 45ml",120,0.045),
("Household","Pest Control","Tortoise Mosquito Coil 10 Pcs",65,0.1),
("Household","Pest Control","All Out Mosquito Liquid Refill 45ml",110,0.045),
("Household","Pest Control","Odonil Room Freshener Spray 220ml",175,0.22),
("Household","Pest Control","Airwick Freshmatic Refill 250ml",350,0.25),

# ── PERSONAL CARE: FOOT CARE ──────────────────────────────────────────────────
("Personal Care","Foot Care","Scholl Velvet Smooth Foot Cream 60ml",325,0.06),
("Personal Care","Foot Care","Himalaya Foot Cream 75g",90,0.075),
("Personal Care","Foot Care","Soulflower Peppermint Foot Scrub 200g",240,0.2),

# ── MORE HOUSEHOLD ────────────────────────────────────────────────────────────
("Household","Paper","Wet Ones Hand Sanitiser Wipes 15 Pcs",120,0.08),
("Household","Sanitiser","Dettol Sanitizer Spray 50ml",95,0.05),
("Household","Sanitiser","Lifebuoy Hand Sanitizer 500ml",185,0.5),
("Household","Sanitiser","Savlon Surface Disinfectant Spray 500ml",230,0.5),
]


def pick_stock():
    r = random.random()
    if r < 0.15:   return random.randint(1, 5)
    elif r < 0.35: return random.randint(6, 15)
    elif r < 0.75: return random.randint(20, 50)
    else:          return random.randint(60, 150)


def main():
    # --- fetch current max product_id number from products2 ---
    print("Connecting to NeonDB...")
    conn = psycopg2.connect(NEON_DSN, connect_timeout=30,
                            cursor_factory=psycopg2.extras.RealDictCursor)
    cur = conn.cursor()

    # Drop and recreate products2 cleanly
    print("Recreating products2 table...")
    cur.execute("DROP TABLE IF EXISTS products2 CASCADE;")
    cur.execute("""
        CREATE TABLE products2 (
            product_id TEXT PRIMARY KEY,
            barcode TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            weight_kg REAL NOT NULL,
            category TEXT NOT NULL,
            sub_category TEXT,
            aisle INT,
            partition_no INT,
            shelf_no TEXT,
            position_tag TEXT,
            side TEXT,
            stock_quantity INT DEFAULT 50,
            reorder_level INT DEFAULT 8,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_p2_barcode ON products2(barcode);
        CREATE INDEX IF NOT EXISTS idx_p2_category ON products2(category);
    """)
    conn.commit()
    print("  ✓ products2 table created")
    cur.close()
    conn.close()

    # Trim/extend to exactly 500
    prods = PRODUCTS2[:500]
    while len(prods) < 500:
        # Cycle through adding variants if needed
        base = PRODUCTS2[len(prods) % len(PRODUCTS2)]
        cat, sub, name, price, wt = base
        variant_name = name.rsplit(' ', 1)[0] + ' (Value Pack)'
        if variant_name not in {p[2] for p in prods}:
            prods.append((cat, sub, variant_name, round(price * 1.8), wt * 2))

    print(f"\nInserting {len(prods)} products into products2...")
    conn = psycopg2.connect(NEON_DSN, connect_timeout=30,
                            cursor_factory=psycopg2.extras.RealDictCursor)
    cur = conn.cursor()
    committed = 0

    for i, (cat, sub, name, price, wt) in enumerate(prods, start=501):
        prod_id = f"PROD{i:05d}"
        barcode = f"89020{i:05d}"
        stock   = pick_stock()

        # Aisle assignment: aisles 1-3, fill sequentially
        aisle  = ((i - 501) // 167) + 1
        if aisle > 3: aisle = 3

        cur.execute("""
            INSERT INTO products2
              (product_id, barcode, name, price, weight_kg, category, sub_category,
               aisle, partition_no, shelf_no, position_tag, side, stock_quantity, reorder_level)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,0,'0.0','P000','Left',%s,8)
            ON CONFLICT (product_id) DO NOTHING
        """, (prod_id, barcode, name, price, wt, cat, sub, aisle, stock))

        committed += 1
        if committed % 25 == 0:
            conn.commit()
            print(f"  Inserted {committed} rows...")

    conn.commit()

    # Final count
    cur.execute("SELECT COUNT(*) as cnt FROM products2")
    total = cur.fetchone()['cnt']
    cur.close()
    conn.close()

    print(f"\n✅ Done! {total} products in products2 (PROD00501-PROD01000)")
    print(f"   Combined with products table: {total + 500} total products")


if __name__ == '__main__':
    main()
