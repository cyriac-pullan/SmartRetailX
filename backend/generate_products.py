
import csv
import os

CSV_PATH = r"m:\Projects\MAJ FIN\database\products_complete.csv"

# Comprehensive list of Supermarket Essentials
new_products_data = [
    # --- PANTRY STAPLES ---
    ("Grains", "Rice", "Basmati Rice 5kg", 600, 5.0, "P301", "50"),
    ("Grains", "Rice", "Sona Masoori Rice 10kg", 550, 10.0, "P301", "30"),
    ("Grains", "Rice", "Brown Rice 1kg", 120, 1.0, "P301", "40"),
    ("Grains", "Flour", "Whole Wheat Atta 5kg", 220, 5.0, "P301", "40"),
    ("Grains", "Flour", "Maida (All Purpose Flour) 1kg", 50, 1.0, "P301", "50"),
    ("Grains", "Flour", "Besan (Gram Flour) 500g", 60, 0.5, "P301", "50"),
    ("Grains", "Flour", "Rava (Semolina) 500g", 45, 0.5, "P301", "50"),
    ("Pulses", "Dal", "Toor Dal 1kg", 160, 1.0, "P302", "50"),
    ("Pulses", "Dal", "Moong Dal Yellow 1kg", 140, 1.0, "P302", "50"),
    ("Pulses", "Dal", "Chana Dal 1kg", 110, 1.0, "P302", "50"),
    ("Pulses", "Dal", "Urad Dal 1kg", 150, 1.0, "P302", "50"),
    ("Pulses", "Beans", "Kabuli Chana 1kg", 180, 1.0, "P302", "40"),
    ("Pulses", "Beans", "Rajma (Red Kidney Beans) 1kg", 170, 1.0, "P302", "40"),
    
    # --- OILS & GHEE ---
    ("Oils", "Cooking", "Sunflower Oil 5L Can", 850, 5.0, "P303", "20"),
    ("Oils", "Cooking", "Mustard Oil 1L", 180, 1.0, "P303", "40"),
    ("Oils", "Cooking", "Groundnut Oil 1L", 210, 1.0, "P303", "40"),
    ("Oils", "Cooking", "Olive Oil Extra Virgin 500ml", 650, 0.5, "P303", "30"),
    ("Oils", "Ghee", "Cow Ghee 500ml", 350, 0.5, "P303", "40"),
    
    # --- SPICES & MASALAS ---
    ("Spices", "Whole", "Cumin Seeds (Jeera) 100g", 40, 0.1, "P304", "100"),
    ("Spices", "Whole", "Mustard Seeds 100g", 20, 0.1, "P304", "100"),
    ("Spices", "Whole", "Black Pepper Whole 50g", 60, 0.05, "P304", "100"),
    ("Spices", "Powder", "Turmeric Powder 200g", 40, 0.2, "P304", "100"),
    ("Spices", "Powder", "Red Chilli Powder 200g", 55, 0.2, "P304", "100"),
    ("Spices", "Powder", "Coriander Powder 200g", 45, 0.2, "P304", "100"),
    ("Spices", "Powder", "Garam Masala 100g", 80, 0.1, "P304", "100"),
    ("Spices", "Masala", "Chicken Masala 100g", 65, 0.1, "P304", "80"),
    ("Spices", "Masala", "Sambar Powder 100g", 50, 0.1, "P304", "80"),
    
    # --- BREAKFAST & CEREALS ---
    ("Breakfast", "Cereal", "Kelloggs Corn Flakes 500g", 180, 0.5, "P305", "40"),
    ("Breakfast", "Cereal", "Chocos 350g", 160, 0.35, "P305", "40"),
    ("Breakfast", "Cereal", "Muesli Fruit & Nut 400g", 280, 0.4, "P305", "30"),
    ("Breakfast", "Oats", "Quaker Oats 1kg", 190, 1.0, "P305", "40"),
    ("Breakfast", "Spread", "Peanut Butter Creamy 350g", 180, 0.35, "P305", "40"),
    ("Breakfast", "Spread", "Fruit Jam Mix 500g", 150, 0.5, "P305", "40"),
    ("Breakfast", "Spread", "Honey 500g Squeeze", 220, 0.5, "P305", "40"),
    
    # --- BAKERY & DAIRY ---
    ("Bakery", "Bread", "Whole Wheat Bread", 50, 0.4, "P306", "20"), # Ensuring generic
    ("Bakery", "Bread", "Multigrain Bread", 60, 0.4, "P306", "20"),
    ("Bakery", "Buns", "Burger Buns 6pc", 45, 0.3, "P306", "20"),
    ("Dairy", "Cheese", "Cheese Slices 10pc", 140, 0.2, "P307", "50"),
    ("Dairy", "Cheese", "Mozzarella Block 200g", 190, 0.2, "P307", "30"),
    ("Dairy", "Butter", "Salted Butter 500g", 270, 0.5, "P307", "40"),
    
    # --- SAUCES & CONDIMENTS ---
    ("Condiments", "Sauce", "Tomato Ketchup 1kg", 130, 1.0, "P308", "50"),
    ("Condiments", "Sauce", "Soy Sauce 200ml", 50, 0.2, "P308", "40"),
    ("Condiments", "Sauce", "Chilli Sauce 200ml", 55, 0.2, "P308", "40"),
    ("Condiments", "Sauce", "Mayonnaise 250g", 85, 0.25, "P308", "40"),
    ("Condiments", "Pickle", "Mango Pickle 500g", 110, 0.5, "P308", "40"),
    
    # --- PASTA & NOODLES ---
    ("Grains", "Pasta", "Penne Pasta 500g", 120, 0.5, "P309", "40"),
    ("Grains", "Pasta", "Spaghetti 500g", 120, 0.5, "P309", "40"),
    ("Grains", "Noodles", "Instant Noodles Masala 4-Pack", 56, 0.28, "P309", "100"),
    ("Grains", "Noodles", "Hakka Noodles 300g", 45, 0.3, "P309", "50"),
    
    # --- BEVERAGES ---
    ("Beverages", "Tea", "Tata Tea Gold 500g", 320, 0.5, "P310", "40"),
    ("Beverages", "Tea", "Green Tea Bags 25pc", 180, 0.05, "P310", "40"),
    ("Beverages", "Coffee", "Nescafe Classic 100g", 300, 0.1, "P310", "40"),
    ("Beverages", "Coffee", "Filter Coffee Powder 500g", 250, 0.5, "P310", "30"),
    ("Beverages", "Juice", "Apple Juice 1L", 130, 1.0, "P310", "30"),
    ("Beverages", "Squash", "Mango Squash 750ml", 160, 0.75, "P310", "30"),
    
    # --- HOUSEHOLD & CLEANING ---
    ("Household", "Laundry", "Washing Machine Liquid 1L", 220, 1.0, "P311", "30"),
    ("Household", "Laundry", "Fabric Conditioner 1L", 200, 1.0, "P311", "30"),
    ("Household", "Cleaning", "Toilet Cleaner 500ml", 95, 0.5, "P311", "40"),
    ("Household", "Cleaning", "Floor Cleaner Pine 1L", 150, 1.0, "P311", "40"),
    ("Household", "Cleaning", "Glass Cleaner Spray 500ml", 110, 0.5, "P311", "30"),
    ("Household", "Dishwash", "Dishwash Liquid Pouch 1L", 180, 1.0, "P311", "40"),
    ("Household", "Dishwash", "Steel Scrubber", 20, 0.02, "P311", "100"),
    ("Household", "Paper", "Toilet Paper 4 Rolls", 160, 0.4, "P312", "30"),
    ("Household", "Paper", "Kitchen Towel 2 Rolls", 120, 0.3, "P312", "30"),
    ("Household", "Paper", "Tissue Box 100 Pulls", 80, 0.1, "P312", "40"),
    ("Household", "Disposables", "Garbage Bags Medium 30pc", 120, 0.2, "P312", "50"),
    ("Household", "Disposables", "Aluminium Foil 9m", 110, 0.1, "P312", "40"),
    
    # --- PERSONAL CARE ---
    ("Personal Care", "Body", "Body Wash Shower Gel 250ml", 190, 0.25, "P313", "30"),
    ("Personal Care", "Body", "Soap Bar 4x100g Value Pack", 150, 0.4, "P313", "40"),
    ("Personal Care", "Hair", "Shampoo Anti-Dandruff 340ml", 310, 0.35, "P313", "30"),
    ("Personal Care", "Hair", "Conditioner 180ml", 210, 0.2, "P313", "30"),
    ("Personal Care", "Hair", "Hair Oil Coconut 200ml", 110, 0.2, "P313", "40"),
    ("Personal Care", "Face", "Face Moisturizer 100ml", 250, 0.1, "P313", "30"),
    ("Personal Care", "Face", "Sunscreen SPF 50 50g", 350, 0.05, "P313", "30"),
    ("Personal Care", "Oral", "Mouthwash 250ml", 140, 0.25, "P313", "30"),
    ("Personal Care", "Hygiene", "Sanitary Pads XL 15pc", 200, 0.1, "P313", "50"),
    ("Personal Care", "Shaving", "Shaving Foam 200ml", 180, 0.2, "P314", "30"),
    ("Personal Care", "Shaving", "Razor 3-Blade Disposable", 60, 0.02, "P314", "50"),
    
    # --- BABY CARE ---
    ("Baby Care", "Diapers", "Diapers Pants M 30pc", 550, 0.8, "P315", "20"),
    ("Baby Care", "Diapers", "Diapers Pants L 30pc", 650, 0.9, "P315", "20"),
    ("Baby Care", "Skin", "Baby Wipes 72pc", 190, 0.4, "P315", "30"),
    ("Baby Care", "Skin", "Baby Lotion 200ml", 220, 0.2, "P315", "30"),
    ("Baby Care", "Skin", "Baby Powder 200g", 150, 0.2, "P315", "30"),
    ("Baby Care", "Food", "Cerelac Wheat Apple 300g", 280, 0.3, "P315", "30"),
    
    # --- SNACKS ---
    ("Snacks", "Biscuits", "Digestive Biscuits 250g", 90, 0.25, "P316", "40"),
    ("Snacks", "Biscuits", "Marie Biscuits 300g", 40, 0.3, "P316", "50"),
    ("Snacks", "Biscuits", "Cream Biscuits Vanilla", 30, 0.1, "P316", "50"),
    ("Snacks", "Chips", "Potato Chips Salted Large", 50, 0.1, "P316", "50"),
    ("Snacks", "Chips", "Nachos Cheese", 60, 0.15, "P316", "50"),
    ("Snacks", "Nuts", "Salted Peanuts 200g", 80, 0.2, "P316", "40"),
    ("Snacks", "Nuts", "Cashews Roasted 100g", 180, 0.1, "P316", "40"),
    ("Snacks", "Nuts", "Almonds Raw 200g", 250, 0.2, "P316", "40"),
    
    # --- CANNED & FROZEN ---
    ("Canned", "Vegetables", "Sweet Corn 400g", 90, 0.4, "P317", "30"),
    ("Canned", "Fruit", "Pineapple Slices 800g", 180, 0.8, "P317", "30"),
    ("Frozen", "Snacks", "French Fries 1kg", 250, 1.0, "P317", "20"),
    ("Frozen", "Snacks", "Veg Burger Patty 10pc", 190, 0.6, "P317", "20"),
    ("Frozen", "Veg", "Green Peas 1kg", 180, 1.0, "P317", "30"),
]

def get_last_ids(csv_path):
    last_prod_id = 0
    last_barcode = 890000000
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pid = row['Product_ID']
                if pid.startswith('PROD'):
                    try:
                        num = int(pid[4:])
                        if num > last_prod_id:
                            last_prod_id = num
                    except:
                        pass
                
                bc = row['Barcode']
                try:
                    bc_num = int(bc)
                    if bc_num > last_barcode:
                        last_barcode = bc_num
                except:
                    pass
    return last_prod_id, last_barcode

last_pid_num, last_barcode_num = get_last_ids(CSV_PATH)
print(f"Starting from ID: PROD{last_pid_num+1:05d}, Barcode: {last_barcode_num+1}")

new_rows = []
current_pid = last_pid_num
current_barcode = last_barcode_num

# Start from aisle 6 since items 1-5 seemed used
aisle_counter = 6 

for category, sub_category, name, price, weight, pos_tag, stock in new_products_data:
    current_pid += 1
    current_barcode += 1
    
    prod_id = f"PROD{current_pid:05d}"
    barcode = str(current_barcode)
    
    # Simple logic for aisle/shelf
    aisle = aisle_counter
    # Alternate aisles every 10 items for variety or group by category
    # But for simplicity, let's just map category to a number or logic
    # The existing data uses aisle 1 for Grains, 2 for Oils etc.
    # We can just increment aisle for new sections or reuse if needed.
    # Let's just put all these in Aisle 6+
    
    row = {
        'Product_ID': prod_id,
        'Barcode': barcode,
        'Product_Name': name,
        'Price': price,
        'Weight_kg': weight,
        'Category': category,
        'Sub_Category': sub_category,
        'Aisle_No': 10, # Generic aisle for new items
        'Partition_No': 200, 
        'Shelf_No': 200.1,
        'Position_Tag': pos_tag,
        'Side': 'Left',
        'Stock_Quantity': stock,
        'Reorder_Level': 5
    }
    new_rows.append(row)

# Append to CSV
with open(CSV_PATH, 'a', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'Product_ID','Barcode','Product_Name','Price','Weight_kg','Category',
        'Sub_Category','Aisle_No','Partition_No','Shelf_No','Position_Tag',
        'Side','Stock_Quantity','Reorder_Level'
    ])
    # header already exists
    for r in new_rows:
        writer.writerow(r)

print(f"Added {len(new_rows)} new products to {CSV_PATH}")
