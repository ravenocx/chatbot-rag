-- --------------------------------------------------------

--
-- Table structure for table rag_configurations
--

CREATE TABLE rag_configurations (
  id BIGSERIAL PRIMARY KEY,
  main_instruction text NOT NULL,
  critical_instruction text NOT NULL,
  additional_guideline text NOT NULL,
  retriever_instruction text NOT NULL,
  top_k_retrieval bigint NOT NULL,
  created_at timestamp NULL DEFAULT NULL,
  updated_at timestamp NULL DEFAULT NULL
);

--
-- Dumping data for table rag_configurations
--

INSERT INTO rag_configurations (id, main_instruction, critical_instruction, additional_guideline, retriever_instruction, top_k_retrieval ,created_at, updated_at) VALUES
(1, 'You are a highly accurate e-commerce chatbot assistant expert. Your main role is to help customers find product information and provide recommendations based **ONLY** on the provided product data.', '1.  **LANGUAGE:** ALWAYS respond in Bahasa Indonesia. The product data provided is also in Bahasa Indonesia - use this data directly without translation.
2.  **DATA ACCURACY:** Base your answer ENTIRELY and SOLELY on the information within the provided data below. Do NOT use any external knowledge or make assumptions about products.
3.  **RELEVANCE FILTER:** ONLY extract and use the specific parts of the product data that are directly relevant to the user''s question, even if the full data contains unrelated information. Ignore any parts of the context that are NOT related to the question.
4.  **NO DISCLAIMERS:** Do NOT include any disclaimers, apologies, or notes like "berdasarkan data yang tersedia" or "data mungkin tidak lengkap" in your answer.', '- If recommending products, explain why based on the available product specifications
- Be specific about product features, prices, and availability as mentioned in the data
- Use a friendly, professional tone typical of Indonesian customer service' , 'Given a user’s product-related query, retrieve the most RELEVANT and informative product descriptions, specifications, or recommendations that directly address the query.', 5 , '2023-03-14 14:09:00', '2024-02-12 06:18:42');

-- --------------------------------------------------------

--
-- Table structure for table admins
--

CREATE TABLE admins (
  id BIGSERIAL PRIMARY KEY,
  uid varchar(100) DEFAULT NULL,
  role_id bigint DEFAULT NULL,
  created_by bigint DEFAULT NULL,
  updated_by bigint DEFAULT NULL,
  name varchar(70) DEFAULT NULL,
  user_name varchar(70) DEFAULT NULL,
  email varchar(70) DEFAULT NULL,
  phone varchar(70) DEFAULT NULL,
  image varchar(120) DEFAULT NULL,
  address varchar(255) DEFAULT NULL,
  password varchar(255) DEFAULT NULL,
  status varchar(1) NOT NULL DEFAULT '1',
  created_at timestamp NULL DEFAULT NULL,
  updated_at timestamp NULL DEFAULT NULL
);

--
-- Dumping data for table admins
--

INSERT INTO admins (id, uid, role_id, created_by, updated_by, name, user_name, email, phone, image, address, password, status, created_at, updated_at) VALUES
(1, NULL, 1, NULL, NULL, 'Admin', 'admin', 'admin@gmail.com', '123123', '65ae633fc7a411705927487.png', NULL, '$2y$10$/rlWCJpoEyTmGjAFwd0bZu8fCRDecKdrEvPo3wXwrRirTcT0SgOw2', '1', '2023-03-14 14:09:00', '2024-02-12 06:18:42');

-- --------------------------------------------------------

--
-- Table structure for table users
--

CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  country_id bigint DEFAULT NULL,
  uid varchar(100) DEFAULT NULL,
  fcm_token text DEFAULT NULL,
  name varchar(255) DEFAULT NULL,
  username varchar(70) DEFAULT NULL,
  last_name varchar(255) DEFAULT NULL,
  email varchar(70) DEFAULT NULL,
  image varchar(100) DEFAULT NULL,
  phone varchar(40) DEFAULT NULL,
  balance numeric(18,8) NOT NULL DEFAULT 0.00000000,
  email_verified_at timestamp NULL DEFAULT NULL,
  last_seen timestamp DEFAULT NULL,
  address text DEFAULT NULL,
  billing_address text DEFAULT NULL,
  google_id varchar(255) DEFAULT NULL,
  point integer NOT NULL DEFAULT 0,
  otp_code integer DEFAULT NULL,
  password varchar(255) NOT NULL,
  status varchar(1) NOT NULL DEFAULT '1',
  remember_token varchar(100) DEFAULT NULL,
  created_at timestamp NULL DEFAULT NULL,
  updated_at timestamp NULL DEFAULT NULL
);

--
-- Dumping data for table users
--

INSERT INTO users (id, country_id, uid, fcm_token, name, username, last_name, email, image, phone, balance, email_verified_at, last_seen, address, billing_address, google_id, point, otp_code, password, status, remember_token, created_at, updated_at) VALUES
(1, NULL, '0V0A-ohKiUJlO-vVrS', NULL, 'Yoga', NULL, NULL, 'customer@gmail.com', NULL, '081775106640', '0.00000000', NULL, '2025-06-26 14:19:44', NULL, NULL, NULL, 0, NULL, '$2y$10$fe6NcTFXtpl9Wrr2pwh7d.Ks5thlwcmncZGddkNwqcBpuaT33ymAa', '1', '50XJYE5wRIIJD6CVAC9acd12shi9zfzqHsdk2TyFOILrxwkytgqEgFDVoi9J', '2025-05-06 18:14:52', '2025-06-26 14:19:45'),
(2, NULL, '7hqP-EI3MEwBw-BV4K', NULL, 'Haris', NULL, NULL, 'haris@gmail.com', NULL, '081775106644', '0.00000000', NULL, '2025-06-22 16:03:45', NULL, NULL, NULL, 0, NULL, '$2y$10$NMGKTZrnVr0dsPMiL7RSduInOF84xmVQ.JPdjHMcandKa/sfMf/n6', '1', 'drrPtxhqrG9Y1gGzGkAlyxgapCUqzqeZ0FSevN725Ds5ZYMc3s0hD13gOuE4', '2025-05-10 16:47:03', '2025-06-22 16:03:46');

SELECT setval('users_id_seq', (SELECT COALESCE(MAX(id), 0) FROM users) + 1, false);
-- --------------------------------------------------------