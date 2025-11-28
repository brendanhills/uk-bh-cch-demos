import streamlit as st

# --- Page Configuration ---
# Set the page to be wide, with a custom title and icon
st.set_page_config(layout="wide", page_title="Cymbal Cosmetics", page_icon="💄")

# --- Custom CSS for Branding ---
# This CSS will inject our custom brand colors, fonts, and styles
def load_css():
    """Injects custom CSS for branding and styling."""
    st.markdown("""
        <style>
            /* Import a clean, modern font */
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

            /* --- Base Styles --- */
            body {
                font-family: 'Montserrat', sans-serif;
            }

            /* --- Brand Title (REMOVED as it's replaced by logo) --- */
            /*
            .brand-title {
                font-size: 2.5rem;
                font-weight: 700;
                color: #B8860B; 
                text-align: center;
                padding: 1rem 0;
            }
            */

            /* --- Product & Price Styles --- */
            .product-header {
                font-size: 2.25rem;
                font-weight: 600;
                color: #333;
            }

            .product-price {
                font-size: 2rem;
                font-weight: 700;
                color: #004D40; /* Dark Teal */
                margin-top: -10px;
            }
            
            .product-saving {
                color: #D9534F; /* A soft red for savings */
                font-weight: 600;
            }
            
            .rating-text {
                color: #555;
                margin-left: 10px;
            }

            /* --- Add to Basket Button --- */
            .stButton > button, .add-to-basket-btn {
                width: 100%;
                background-color: #004D40; /* Dark Teal */
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-size: 1.1rem;
                font-weight: 600;
                text-align: center;
                text-decoration: none; /* For link-based button */
                display: inline-block; /* For link-based button */
                transition: background-color 0.3s ease, transform 0.1s ease;
                cursor: pointer; /* Ensure pointer cursor */
            }

            .stButton > button:hover, .add-to-basket-btn:hover {
                background-color: #00695C; /* Slightly lighter teal on hover */
                color: white; /* Ensure text color stays white */
                transform: scale(1.02);
            }
            
            /* --- Review Box --- */
            .review-box {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 12px;
                background-color: #FAFAFA;
            }
            
            .review-author {
                font-weight: 700;
                color: #333;
            }

        </style>
    """, unsafe_allow_html=True)

# --- Load the CSS ---
load_css()

# --- Header ---
# Center the logo image
_ , logo_col, _ = st.columns([1,1,1])
with logo_col:
     st.image(
         "https://googleusercontent.com/image_generation_content/0", # Cymbal Cosmetics Logo
         use_container_width=True
     )
# st.markdown("<h1 class='brand-title'>Cymbal Cosmetics</h1>", unsafe_allow_html=True) # Replaced by logo
st.divider()

# --- Main Product Section (Two Columns) ---
col1, col2 = st.columns([2, 3])  # Image column, Info column

# --- Column 1: Product Image ---
with col1:
    # Use the generated product image
    st.image(
        "https://googleusercontent.com/image_generation_content/1", # Luxe Satin Lipstick
        use_container_width=True,
        caption="Cymbal Luxe Satin Lipstick in 'Rose Petal'"
    )

# --- Column 2: Product Details & Actions ---
with col2:
    st.caption("LIPSTICK / SATIN FINISH / NEW")
    
    # Using markdown for custom styling
    st.markdown("<h2 class'product-header'>Luxe Satin Lipstick</h2>", unsafe_allow_html=True)
    
    # Rating
    st.markdown(
        "<span>⭐⭐⭐⭐☆</span> <span class='rating-text'>(128 Reviews)</span>", 
        unsafe_allow_html=True
    )
    
    # Price
    st.markdown("<p class='product-price'>£22.00</p>", unsafe_allow_html=True)
    st.markdown(
        "<span class='product-saving'>Save £4.00</span> (Was £26.00)", 
        unsafe_allow_html=True
    )
    
    st.caption("SKU: C-LS-102")
    
    # Special Offer
    st.success("✨ **Special Offer:** Buy 2, get 1 free on all lipsticks!")
    
    # Shade Selector
    shade = st.selectbox(
        "**Select Shade:**",
        ["Rose Petal (featured)", "Brave Red", "Coral Kiss", "Nude Blush", "Deep Dahlia"],
        index=0  # Default to the first item
    )
    
    # Add to Basket Button
    # We use a simple button and style it with the .stButton selector
    if st.button("Add to Basket"):
        # This is where you would add the logic to add to a cart
        st.toast(f"Added '{shade}' to your basket!", icon="💄")
    
    # Payment Options
    st.markdown("<br><small>Pay in 3 with Klarna. Collect 22 loyalty points.</small>", unsafe_allow_html=True)

    # Find in Store
    st.link_button("Find in Store", "#")

st.divider()

# --- Lower Section: Product Information ---
st.subheader("Product Description")
st.write(
    """
    Indulge your lips with the **Cymbal Luxe Satin Lipstick**. 
    This innovative formula combines rich, buildable pigment with a creamy, hydrating texture
    for a smooth, satin finish that lasts all day. 
    
    Infused with Vitamin E and Jojoba Oil, it glides on effortlessly, nourishing your
    lips while delivering stunning, multi-dimensional color.
    """
)

# --- More Details in Tabs ---
tab1, tab2, tab3 = st.tabs(["How to Use", "Ingredients", "Customer Reviews"])

with tab1:
    st.markdown(
        """
        1.  **Exfoliate:** Start with a smooth canvas. Gently exfoliate your lips if needed.
        2.  **Define:** (Optional) Line your lips with a matching Cymbal Lip Liner for a precise shape.
        3.  **Apply:** Glide the lipstick directly from the bullet, starting at the center of your
            upper lip and moving outward. Repeat on the lower lip.
        4.  **Perfect:** Press your lips together to evenly distribute the color.
        """
    )

with tab2:
    st.markdown("##### Full Ingredient List:")
    st.text(
        """
        Ricinus Communis (Castor) Seed Oil, Simmondsia Chinensis (Jojoba) Seed Oil, 
        Caprylic/Capric Triglyceride, Euphorbia Cerifera (Candelilla) Wax, 
        Cera Alba (Beeswax), Tocopherol (Vitamin E), May Contain (+/-): 
        Titanium Dioxide (CI 77891), Iron Oxides (CI 77491, CI 77492, CI 77499), 
        Red 7 Lake (CI 15850), Blue 1 Lake (CI 42090).
        
        *Vegan, Cruelty-Free, Paraben-Free.*
        """
    )

with tab3:
    st.markdown("##### What people are saying...")
    
    # Review 1
    st.markdown(
        """
        <div class='review-box'>
            <span class='review-author'>Sarah J.</span> - ⭐⭐⭐⭐⭐
            <p>Absolutely obsessed! The 'Nude Blush' shade is my new holy grail. 
            It feels so hydrating and doesn't feather at all. 10/10!</p>
        </div>
        """, unsafe_allow_html=True
    )
    
    # Review 2
    st.markdown(
        """
        <div class='review-box'>
            <span class='review-author'>Michelle T.</span> - ⭐⭐⭐⭐☆
            <p>Beautiful color ('Brave Red') and very comfortable to wear. 
            It's not 100% transfer-proof, but the lasting power is still very good
            for a satin formula. Would buy again.</p>
        </div>
        """, unsafe_allow_html=True
    )



