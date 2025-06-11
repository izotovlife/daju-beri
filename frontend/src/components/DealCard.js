// src/components/DealsList.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Box, Button, Grid, Paper, Typography } from '@mui/material';

const DealsList = () => {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    async function fetchDeals() {
      setLoading(true);
      try {
        const response = await axios.get(`http://localhost:8000/api/deals/?page=${page}`);
        setDeals([...deals, ...response.data.results]);
        setTotalPages(Math.ceil(response.data.count / 10)); // Предполагая, что страница выдает по 10 записей
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchDeals();
  }, [page]);

  const handleLoadMore = () => {
    if (!loading && page < totalPages) {
      setPage(page + 1);
    }
  };

  return (
    <>
      <Box sx={{ p: 2 }} m={2}>
        <Button disabled={loading || page === totalPages} onClick={handleLoadMore}>
          Показать еще
        </Button>
      </Box>
      <Grid container spacing={2}>
        {deals.map((deal) => (
          <Grid item xs={12} sm={6} md={4} key={deal.id}>
            {/* Вставьте сюда карточку акции */}
          </Grid>
        ))}
      </Grid>
    </>
  );
};

export default DealsList;