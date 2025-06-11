// src/services/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const fetchProducts = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/products`);
    return response.data;
  } catch (error) {
    throw new Error('Failed to fetch products');
  }
};