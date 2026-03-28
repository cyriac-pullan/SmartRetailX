import pandas as pd
import random
import subprocess
import os
import speech_recognition as sr


class SmartRetailXVoice:
    def __init__(self):
        self.df = None
        self.recognizer = sr.Recognizer()  # recognizer for microphone
        self.load_dataset()

        # try adjusting noise level once
        try:
            with sr.Microphone() as mic:
                self.recognizer.adjust_for_ambient_noise(mic, duration=0.7)
        except:
            pass

    def load_dataset(self):
        """Load the store layout dataset"""
        import os
        try:
            csv_path = os.path.join(os.path.dirname(__file__), "..", "database", "products_unique_remapped.csv")
            self.df = pd.read_csv(csv_path)
            self.df.columns = self.df.columns.str.strip()

            # Normalize columns safely using .str accessors
            self.df["Position_Tag"] = self.df["Position_Tag"].astype(str).str.strip().str.lower()
            self.df["Product_Name"] = self.df["Product_Name"].astype(str).str.strip()

            print("✅ Dataset loaded successfully!")
            # protect if Aisle_No column missing or not numeric
            try:
                aisles = self.df['Aisle_No'].nunique()
            except Exception:
                aisles = "N/A"
            print(f"📊 Loaded {len(self.df)} products across {aisles} aisles")

        except FileNotFoundError:
            print("❌ Error: store_layout.csv file not found!")
            print("💡 Please place the file in the same directory.")
            exit()
        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
            exit()

    def speak(self, text):
        """Use macOS built-in 'say' command for text-to-speech"""
        try:
            clean = text.replace('🔥', '').replace('🛒', '').replace('⭐', '').replace('💥', '') \
                        .replace('✨', '').replace('🎯', '').replace('📢', '')
            subprocess.run(['say', clean])
        except Exception:
            print(f"(Voice output unavailable: {text})")

    def listen(self, prompt_text="Say a product name or say 'text' to type:",
               timeout=5, phrase_time_limit=6, api_mode=False):

        print("\n🎤 VOICE LISTENING...")
        print(prompt_text)

        try:
            with sr.Microphone() as mic:
                try:
                    self.recognizer.adjust_for_ambient_noise(mic, duration=0.5)
                except:
                    pass

                print("🎙 Listening...")
                audio = self.recognizer.listen(
                    mic, timeout=timeout, phrase_time_limit=phrase_time_limit
                )

                try:
                    text = self.recognizer.recognize_google(audio).strip()
                    print(f"🗣 You said: {text}")

                    if text.lower() in ["text", "type"]:
                        if api_mode: return None
                        return input("🔍 Type product name: ").strip()

                    return text

                except sr.UnknownValueError:
                    print("❌ Could not understand speech.")
                    if api_mode: return None
                    typed = input("🔍 Type product name (or Enter to retry voice): ").strip()
                    return typed if typed else ""

                except sr.RequestError:
                    print("⚠️ Speech service error — using typing instead.")
                    if api_mode: return None
                    return input("🔍 Type product name: ").strip()

        except Exception as e:
            print(f"⚠️ Microphone error: {e}")
            if api_mode: return None
            return input("🔍 Type product name: ").strip()

    def search_products(self, search_term):
        search_term = search_term.lower().strip()
        return self.df[self.df['Product_Name'].str.lower().str.contains(search_term, na=False)]

    def voice_search_feature(self):
        print("\n🎤 VOICE PRODUCT SEARCH")
        print("-" * 40)
        self.speak("Voice search activated. Please tell me the product name.")

        while True:
            search_term = self.listen()

            if isinstance(search_term, str) and search_term.lower() == "back":
                self.speak("Returning to menu.")
                break

            if not search_term:
                self.speak("Say the product again.")
                continue

            print(f"\n🔍 Searching for: {search_term}")
            results = self.search_products(search_term)

            if not results.empty:
                unique = results.drop_duplicates(subset=['Product_Name'])
                self.speak(f"I found {len(unique)} matching items.")

                print(f"\n✅ Found {len(unique)} products:")
                print("-" * 70)

                spoken = 0
                for i, (_, p) in enumerate(unique.head(5).iterrows(), 1):
                    loc = f"Aisle {p.get('Aisle_No', 'N/A')} | {p.get('Side', 'N/A')} | Shelf {p.get('Shelf_No', 'N/A')}"
                    print(f"{i}. {p['Product_Name']}")
                    print(f"   📍 {loc}")
                    print(f"   🏷 Position: {str(p.get('Position_Tag','')).upper()}\n")

                    if spoken < 3:
                        self.speak(f"{p['Product_Name']} at {loc}")
                        spoken += 1

                if len(unique) > 3:
                    self.speak(f"And {len(unique)-3} more items available.")

                try:
                    self.suggest_ad_product(search_term, results)
                except Exception as e:
                    print(f"⚠️ Ad suggestion error: {e}")

            else:
                self.speak("No matching products found.")
                print("❌ No products found!")
                self.suggest_similar_products(search_term)

    def suggest_similar_products(self, search_term):
        if not isinstance(search_term, str):
            return
        search_term = search_term.lower()
        words = search_term.split()

        print("\n💡 Suggestions:")
        suggestions = []

        for w in words:
            if len(w) > 2:
                similar = self.df[self.df['Product_Name'].str.lower().str.contains(w, na=False)]
                if not similar.empty:
                    suggestions.extend(similar['Product_Name'].unique()[:2])

        if suggestions:
            for s in list(dict.fromkeys(suggestions))[:5]:
                print(f"   • {s}")
            self.speak("Showing similar product suggestions.")
        else:
            print("   No similar items. Try another search.")
            self.speak("Try a different word.")

    def voice_ads_feature(self):
        print("\n📍 VOICE-ENABLED ADVERTISEMENTS")
        self.speak("Enter your shelf position for advertisements.")

        while True:
            position = input("🎯 Enter position tag (or 'back'): ").strip().lower()

            if position == "back":
                self.speak("Returning to menu")
                break

            self.show_voice_ad(position)

    def show_voice_ad(self, position_tag):
        position_tag = position_tag.lower()

        matching_positions = []
        if "/" not in position_tag:
            for pos in self.df["Position_Tag"].unique():
                if "/" in pos and position_tag in pos.split("/"):
                    matching_positions.append(pos)
        else:
            matching_positions = [position_tag]

        if not matching_positions:
            print("❌ No products found for that position.")
            self.speak("No products found for this location.")
            return

        all_products = pd.DataFrame()
        for pos in matching_positions:
            all_products = pd.concat([all_products, self.df[self.df["Position_Tag"] == pos]])

        product = all_products.sample(1).iloc[0]

        p_name = product["Product_Name"]
        aisle = product["Aisle_No"]
        shelf = product["Shelf_No"]
        side = product["Side"]
        tag = str(product["Position_Tag"]).upper()

        templates = [
            f"🔥 Special Offer! Get {p_name} at Aisle {aisle}, {side} side, Shelf {shelf}.",
            f"🛒 Exclusive Deal on {p_name}! Find it in Aisle {aisle}.",
            f"⭐ Don't miss out on {p_name}! It's available at Shelf {shelf}.",
            f"💥 Bonanza! {p_name} now at position {tag}.",
            f"✨ Great savings on {p_name}! Located at Aisle {aisle}.",
        ]

        ad = random.choice(templates)

        print("\n📢 ADVERTISEMENT")
        print("=" * 70)
        print(ad)
        print("=" * 70)

        self.speak(ad)

    def suggest_ad_product(self, search_term, results):
        search_term = str(search_term).lower().strip()

        try:
            pool = self.df[~self.df['Product_Name'].str.lower().str.contains(search_term, na=False)].copy()
        except Exception:
            pool = self.df.copy()

        if pool.empty:
            return

        try:
            if 'Brand' in self.df.columns:
                found_brands = results['Brand'].dropna().unique().tolist()
                if found_brands:
                    pool = pool[~pool['Brand'].isin(found_brands)]
        except Exception:
            pass

        candidates = pd.DataFrame()
        try:
            tags = results['Position_Tag'].dropna().unique().tolist() if 'Position_Tag' in results.columns else []
            for t in tags:
                matches = pool[pool['Position_Tag'] == t]
                if not matches.empty:
                    candidates = pd.concat([candidates, matches])

            if candidates.empty and 'Aisle_No' in results.columns:
                aisles = results['Aisle_No'].dropna().unique().tolist()
                for a in aisles:
                    matches = pool[pool['Aisle_No'] == a]
                    if not matches.empty:
                        candidates = pd.concat([candidates, matches])

            if candidates.empty:
                words = [w for w in search_term.split() if len(w) > 2]
                for w in words:
                    matches = pool[pool['Product_Name'].str.lower().str.contains(w, na=False)]
                    if not matches.empty:
                        candidates = pd.concat([candidates, matches])

        except Exception:
            candidates = pool

        if candidates.empty:
            candidates = pool

        try:
            candidates = candidates.drop_duplicates(subset=['Product_Name'])
            ad_product = candidates.sample(1).iloc[0]
        except Exception:
            return

        try:
            ad_name = ad_product.get('Product_Name', 'Special product')
            ad_brand = ad_product.get('Brand', None)
            aisle = ad_product.get('Aisle_No', 'N/A')
            shelf = ad_product.get('Shelf_No', 'N/A')
            side = ad_product.get('Side', 'N/A')
            pos = str(ad_product.get('Position_Tag', '')).upper()

            if ad_brand and str(ad_brand).strip():
                ad_text = f"✨ Recommended alternative: {ad_name} by {ad_brand} — Aisle {aisle}, {side} side, Shelf {shelf}."
            else:
                ad_text = f"✨ Recommended alternative: {ad_name} — Aisle {aisle}, {side} side, Shelf {shelf}."

            print("\n📣 RECOMMENDED PRODUCT (Sponsored)")
            print("-" * 70)
            print(ad_text)
            print("-" * 70)

            try:
                self.speak(f"Recommended alternative: {ad_name} at Aisle {aisle}.")
            except Exception:
                pass

        except Exception:
            return

    def store_statistics_voice(self):
        print("\n📊 STORE STATISTICS")
        self.speak("Here are store statistics.")

        total_products = len(self.df)
        try:
            aisles = self.df['Aisle_No'].nunique()
        except Exception:
            aisles = "N/A"

        print(f"📦 Total products: {total_products}")
        print(f"🏪 Total aisles: {aisles}")
        print(f"📍 Unique positions: {self.df['Position_Tag'].nunique()}")

        self.speak(f"The store has {total_products} products across {aisles} aisles.")

    def text_only_mode(self):
        print("\n🔇 TEXT-ONLY MODE")

        while True:
            term = input("Enter product to search (or 'back'): ").strip()

            if term.lower() == "back":
                break

            results = self.search_products(term)

            if not results.empty:
                for _, p in results.head(10).iterrows():
                    loc = f"Aisle {p['Aisle_No']} | {p['Side']} | Shelf {p['Shelf_No']}"
                    print(f"- {p['Product_Name']} → {loc}")
            else:
                print("❌ No products found.")

    def run(self):
        self.speak("Welcome to Smart Retail X Voice Assistant.")

        while True:
            print("\n" + "=" * 70)
            print("🎤 SMART RETAIL X - VOICE ASSISTANT")
            print("=" * 70)

            print("1️⃣  Voice Search Products")
            print("2️⃣  Voice Ads (Location Based)")
            print("3️⃣  Store Statistics")
            print("4️⃣  Text-only mode")
            print("5️⃣  Exit")

            choice = input("\nEnter choice: ").strip()

            if choice == "1":
                self.voice_search_feature()
            elif choice == "2":
                self.voice_ads_feature()
            elif choice == "3":
                self.store_statistics_voice()
            elif choice == "4":
                self.text_only_mode()
            elif choice == "5":
                self.speak("Thank you for using Smart Retail X. Goodbye!")
                break
            else:
                print("❌ Invalid choice.")

    # --- ADDED FOR FLASK API INTEGRATION ---
    def api_voice_search(self):
        """Headless version to be called by Flask API"""
        print("\n🎤 API VOICE PRODUCT SEARCH Triggered")

        search_term = self.listen(prompt_text="API waiting for speech input", api_mode=True, timeout=3, phrase_time_limit=4)

        if not search_term:
            return {"success": False, "message": "Could not understand or no speech detected"}

        results = self.search_products(search_term)

        if not results.empty:
            unique = results.drop_duplicates(subset=['Product_Name'])
            top_match = unique.iloc[0]
            loc = f"Aisle {top_match.get('Aisle_No', 'N/A')} | {top_match.get('Side', 'N/A')} | Shelf {top_match.get('Shelf_No', 'N/A')}"

            return {
                "success": True,
                "term": search_term,
                # Return the RAW spoken term so the frontend search box
                # gets "milk" not "Amul Milk 500ml"
                "product_name": search_term,
                "top_match": top_match['Product_Name'],
                "barcode": top_match.get('Barcode', ''),
                "price": float(top_match.get('Price', 0)) if not pd.isna(top_match.get('Price', 0)) else 0,
                "location": loc,
                "count": len(unique)
            }
        else:
            return {"success": False, "message": f"No products found for '{search_term}'"}

if __name__ == "__main__":
    app = SmartRetailXVoice()
    app.run()
