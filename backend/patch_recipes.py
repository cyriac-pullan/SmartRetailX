"""Patch RECIPE_DB with exact DB-matched ingredient names."""
import re

path = r"m:\Projects\MAJ FIN LAT\MAJ FIN\backend\app.py"
content = open(path, "r", encoding="utf-8").read()

# Key: dish name  Value: list of ingredient search terms that match real DB products
# Terms chosen to match real products found in product_check.txt
NEW_RECIPE_DB = r'''RECIPE_DB = {
    # ── Indian Mains ──────────────────────────────────────
    "biryani": ["Fresho Chicken Breast", "Daawat Rozana Basmati Rice", "Amul Pure Ghee", "Epigamia Greek Yogurt", "Fresh Ginger", "Garlic", "Fresh Mint", "Cardamom Green", "Black Pepper Whole", "Annapurna Salt"],
    "chicken biryani": ["Fresho Chicken Breast", "Daawat Rozana Basmati Rice", "Amul Pure Ghee", "Epigamia Greek Yogurt", "Fresh Ginger", "Garlic", "Fresh Mint", "Cardamom Green", "Annapurna Salt"],
    "mutton biryani": ["MDH Mutton Masala", "Daawat Rozana Basmati Rice", "Amul Pure Ghee", "Epigamia Greek Yogurt", "Fresh Ginger", "Garlic", "Fresh Mint", "Annapurna Salt"],
    "veg biryani": ["Daawat Rozana Basmati Rice", "Amul Pure Ghee", "Epigamia Greek Yogurt", "Fresh Ginger", "Garlic", "Fresh Mint", "Annapurna Salt"],
    "butter chicken": ["Fresho Chicken Breast", "Amul Salted Butter", "Amul Fresh Cream", "Amul Taaza Toned Milk", "Garlic", "Fresh Ginger", "Kissan Tomato Ketchup", "Annapurna Salt"],
    "chicken curry": ["Fresho Chicken Breast", "Garlic", "Fresh Ginger", "Amul Pure Ghee", "Annapurna Salt", "Epigamia Greek Yogurt"],
    "chicken tikka masala": ["Fresho Chicken Breast", "Epigamia Greek Yogurt", "Amul Fresh Cream", "Amul Salted Butter", "Garlic", "Fresh Ginger", "Annapurna Salt"],
    "dal makhani": ["Bb Royal Masoor Dal", "Amul Salted Butter", "Amul Fresh Cream", "Garlic", "Fresh Ginger", "Annapurna Salt"],
    "dal tadka": ["Chana Dal", "Garlic", "Fresh Ginger", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "palak paneer": ["Amul Fresh Paneer", "Amul Salted Butter", "Amul Fresh Cream", "Garlic", "Fresh Ginger", "Annapurna Salt"],
    "paneer butter masala": ["Amul Fresh Paneer", "Amul Salted Butter", "Amul Fresh Cream", "Garlic", "Fresh Ginger", "Annapurna Salt"],
    "paneer tikka": ["Amul Fresh Paneer", "Epigamia Greek Yogurt", "Garlic", "Fresh Ginger", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "shahi paneer": ["Amul Fresh Paneer", "Amul Fresh Cream", "Amul Salted Butter", "Nutraj Cashews", "Cardamom Green", "Annapurna Salt"],
    "chole": ["Chana Dal", "Garlic", "Fresh Ginger", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "rajma": ["Black Eyed Peas Lobia", "Garlic", "Fresh Ginger", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "aloo gobi": ["Garlic", "Fresh Ginger", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "fish curry": ["Catla Fish Fillet", "Garlic", "Fresh Ginger", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "fish fry": ["Catla Fish Fillet", "Garlic", "Fresh Ginger", "Fortune Refined Soyabean Oil", "Annapurna Salt", "Black Pepper Whole"],
    "prawn curry": ["Prawns Medium", "Garlic", "Fresh Ginger", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "korma": ["Fresho Chicken Breast", "Epigamia Greek Yogurt", "Amul Fresh Cream", "Nutraj Cashews", "Amul Pure Ghee", "Cardamom Green", "Annapurna Salt"],
    "keema": ["Garlic", "Fresh Ginger", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "sambar": ["Bb Royal Masoor Dal", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "rasam": ["Garlic", "Black Pepper Whole", "Annapurna Salt", "Fortune Refined Soyabean Oil"],
    # ── Breads & Breakfast ─────────────────────────────────
    "dosa": ["Double Horse Idli Rice", "Bb Royal Masoor Dal", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "masala dosa": ["Double Horse Idli Rice", "Bb Royal Masoor Dal", "Fortune Refined Soyabean Oil", "Annapurna Salt", "Fresh Ginger"],
    "idli": ["Double Horse Idli Rice", "Bb Royal Masoor Dal", "Annapurna Salt"],
    "pav bhaji": ["Bonn Multigrain Bread", "Amul Salted Butter", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "vada pav": ["Bonn Multigrain Bread", "Garlic", "Fortune Refined Soyabean Oil", "Annapurna Salt", "Fresh Ginger"],
    "poha": ["Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "upma": ["Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "paratha": ["Aashirvaad Multigrain Atta", "Amul Pure Ghee", "Annapurna Salt"],
    "aloo paratha": ["Aashirvaad Multigrain Atta", "Amul Pure Ghee", "Garlic", "Annapurna Salt"],
    "roti": ["Aashirvaad Multigrain Atta", "Amul Pure Ghee", "Annapurna Salt"],
    "naan": ["Aashirvaad Multigrain Atta", "Epigamia Greek Yogurt", "Amul Taaza Toned Milk", "Amul Salted Butter", "Garlic", "Annapurna Salt"],
    "puri": ["Aashirvaad Multigrain Atta", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "samosa": ["Aashirvaad Multigrain Atta", "Fresh Ginger", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "pakora": ["Fortune Rice Flour", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    # ── Rice Dishes ────────────────────────────────────────
    "pulao": ["Daawat Rozana Basmati Rice", "Amul Pure Ghee", "Annapurna Salt"],
    "khichdi": ["Daawat Rozana Basmati Rice", "Bb Royal Masoor Dal", "Amul Pure Ghee", "Annapurna Salt"],
    "curd rice": ["Daawat Rozana Basmati Rice", "Epigamia Greek Yogurt", "Amul Taaza Toned Milk", "Annapurna Salt"],
    "lemon rice": ["Daawat Rozana Basmati Rice", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "fried rice": ["Daawat Rozana Basmati Rice", "Country Eggs", "Kikkoman Soy Sauce", "Fortune Refined Soyabean Oil", "Garlic", "Annapurna Salt"],
    # ── Sweets ─────────────────────────────────────────────
    "halwa": ["Amul Pure Ghee", "Amul Taaza Toned Milk", "Nutraj Cashews", "Nutraj Raisins", "Cardamom Green", "Madhur Pure Sugar"],
    "kheer": ["Daawat Rozana Basmati Rice", "Amul Taaza Toned Milk", "Madhur Pure Sugar", "Cardamom Green", "Nutraj Cashews", "Nutraj Raisins"],
    "gulab jamun": ["Amul Taaza Toned Milk", "Aashirvaad Multigrain Atta", "Madhur Pure Sugar", "Amul Pure Ghee", "Cardamom Green"],
    "rasgulla": ["Amul Taaza Toned Milk", "Madhur Pure Sugar"],
    "payasam": ["Amul Taaza Toned Milk", "Daawat Rozana Basmati Rice", "Madhur Pure Sugar", "Nutraj Cashews", "Nutraj Raisins", "Amul Pure Ghee", "Cardamom Green"],
    "gajar ka halwa": ["Amul Taaza Toned Milk", "Madhur Pure Sugar", "Amul Pure Ghee", "Nutraj Cashews", "Cardamom Green"],
    # ── International ──────────────────────────────────────
    "pasta": ["Barilla Penne Pasta", "Amul Cheese Slices", "Garlic", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "sandwich": ["Bonn Multigrain Bread", "Amul Cheese Slices", "Amul Salted Butter", "Hellmanns Real Mayonnaise", "Kissan Tomato Ketchup"],
    "omelette": ["Country Eggs", "Amul Taaza Toned Milk", "Fortune Refined Soyabean Oil", "Annapurna Salt", "Black Pepper Whole"],
    "pancakes": ["Aashirvaad Multigrain Atta", "Amul Taaza Toned Milk", "Madhur Pure Sugar", "Amul Salted Butter", "Dabur Honey", "Country Eggs"],
    "french fries": ["Fortune Refined Soyabean Oil", "Annapurna Salt", "Kissan Tomato Ketchup"],
    "burger": ["Bonn Multigrain Bread", "Fresho Chicken Breast", "Amul Cheese Slices", "Hellmanns Real Mayonnaise", "Kissan Tomato Ketchup", "Amul Salted Butter"],
    "pizza": ["Aashirvaad Multigrain Atta", "Amul Mozzarella Cheese", "Fortune Refined Soyabean Oil", "Annapurna Salt"],
    "noodles": ["Chings Secret Hakka Noodles", "Kikkoman Soy Sauce", "Garlic", "Fortune Refined Soyabean Oil", "Annapurna Salt", "Country Eggs"],
    "fried chicken": ["Fresho Chicken Breast", "Country Eggs", "Aashirvaad Multigrain Atta", "Fortune Refined Soyabean Oil", "Annapurna Salt", "Black Pepper Whole"],
    "scrambled eggs": ["Country Eggs", "Amul Salted Butter", "Amul Taaza Toned Milk", "Annapurna Salt", "Black Pepper Whole"],
    "salad": ["Fortune Refined Soyabean Oil", "Annapurna Salt", "Black Pepper Whole"],
    # ── Drinks ─────────────────────────────────────────────
    "tea": ["Amul Taaza Toned Milk", "Madhur Pure Sugar"],
    "coffee": ["Amul Taaza Toned Milk", "Madhur Pure Sugar"],
    "lassi": ["Epigamia Greek Yogurt", "Amul Taaza Toned Milk", "Madhur Pure Sugar", "Annapurna Salt", "Cardamom Green"],
    "milkshake": ["Amul Taaza Toned Milk", "Madhur Pure Sugar"],
    "lemonade": ["Madhur Pure Sugar", "Annapurna Salt"],
    "chaas": ["Epigamia Greek Yogurt", "Annapurna Salt"],
    # ── Snacks ─────────────────────────────────────────────
    "bread omelette": ["Bonn Multigrain Bread", "Country Eggs", "Amul Salted Butter", "Annapurna Salt", "Black Pepper Whole"],
    "fruit salad": ["Madhur Pure Sugar", "Amul Taaza Toned Milk"],
    "curry": ["Bb Royal Masoor Dal", "Fortune Refined Soyabean Oil", "Garlic", "Fresh Ginger", "Annapurna Salt"],
}'''

# Replace old RECIPE_DB block using regex (non-greedy match to end of dict)
pattern = r"RECIPE_DB = \{.*?\}"
new_content = re.sub(pattern, NEW_RECIPE_DB, content, flags=re.DOTALL)

if new_content == content:
    print("ERROR: Pattern not found — no changes made")
else:
    open(path, "w", encoding="utf-8").write(new_content)
    print("SUCCESS: RECIPE_DB updated with exact product-matched ingredients")
