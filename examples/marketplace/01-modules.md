# Functional Modules & Domain Entities

This document details the functional domains and entity boundaries.

## Domain Entities Summary

| Model | Table | Fields | Relations | State Machine |
| :--- | :--- | :--- | :--- | :--- |
| **User** | `users` | 5 | 4 | No |
| **VendorProfile** | `vendor_profiles` | 7 | 2 | No |
| **Category** | `categories` | 4 | 1 | No |
| **Product** | `products` | 9 | 4 | No |
| **Order** | `orders` | 7 | 3 | Yes |
| **OrderItem** | `order_items` | 6 | 2 | No |
| **Payment** | `payments` | 13 | 2 | Yes |
| **Review** | `reviews` | 5 | 2 | No |

## Module Structure

### User Module
- **Database Table**: `users`
- **Purpose**: Encapsulates domain logic for `User` entities.
- **Key Attributes**: `id`, `name`, `email`, `phone`, `avatar`
- **Associated Relations**: `vendor_profile`, `orders`, `payments`, `reviews`

### VendorProfile Module
- **Database Table**: `vendor_profiles`
- **Purpose**: Encapsulates domain logic for `VendorProfile` entities.
- **Key Attributes**: `id`, `user_id`, `shop_name`, `slug`, `description`
- **Associated Relations**: `user`, `products`

### Category Module
- **Database Table**: `categories`
- **Purpose**: Encapsulates domain logic for `Category` entities.
- **Key Attributes**: `id`, `name`, `slug`, `description`
- **Associated Relations**: `products`

### Product Module
- **Database Table**: `products`
- **Purpose**: Encapsulates domain logic for `Product` entities.
- **Key Attributes**: `id`, `vendor_id`, `category_id`, `title`, `slug`
- **Associated Relations**: `vendor`, `category`, `order_items`, `reviews`

### Order Module
- **Database Table**: `orders`
- **Purpose**: Encapsulates domain logic for `Order` entities.
- **Key Attributes**: `id`, `customer_id`, `order_number`, `subtotal_amount`, `tax_amount`
- **Associated Relations**: `customer`, `items`, `payments`

### OrderItem Module
- **Database Table**: `order_items`
- **Purpose**: Encapsulates domain logic for `OrderItem` entities.
- **Key Attributes**: `id`, `order_id`, `product_id`, `quantity`, `unit_price`
- **Associated Relations**: `order`, `product`

### Payment Module
- **Database Table**: `payments`
- **Purpose**: Encapsulates domain logic for `Payment` entities.
- **Key Attributes**: `id`, `order_id`, `user_id`, `gateway`, `amount`
- **Associated Relations**: `order`, `user`

### Review Module
- **Database Table**: `reviews`
- **Purpose**: Encapsulates domain logic for `Review` entities.
- **Key Attributes**: `id`, `product_id`, `customer_id`, `rating`, `comment`
- **Associated Relations**: `product`, `customer`
