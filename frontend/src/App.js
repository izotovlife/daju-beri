//C:\Users\ASUS Vivobook\PycharmProjects\PythonProject\daju-beri\frontend\src\App.js

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Grid, Card, CardContent, CardMedia, Typography } from '@mui/material';

function App() {
  const [deals, setDeals] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8000/api/deals/')
      .then(response => {
        setDeals(response.data);
      })
      .catch(error => {
        console.error('Ошибка при загрузке данных:', error);
      });
  }, []);

  return (
    <Container>
      <Typography variant="h2" gutterBottom align="center">
        🔥 Дают-Бери: Лучшие акции
      </Typography>

      <Grid container spacing={3}>
        {deals.map(deal => (
          <Grid item xs={12} sm={6} md={4} key={deal.id}>
            <Card>
              {deal.image_url && (
                <CardMedia
                  component="img"
                  height="200"
                  image={deal.image_url}
                  alt={deal.title}
                />
              )}
              <CardContent>
                <Typography variant="h5">{deal.title}</Typography>
                <Typography color="textSecondary">
                  {deal.marketplace}
                </Typography>
                <Typography variant="body2">
                  <span style={{ textDecoration: 'line-through' }}>
                    {deal.original_price} руб.
                  </span>
                  {' → '}
                  <span style={{ color: 'red', fontWeight: 'bold' }}>
                    {deal.discount_price} руб.
                  </span>
                  <span style={{ marginLeft: 10, color: 'green' }}>
                    (-{deal.discount_percentage}%)
                  </span>
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Действует до: {new Date(deal.valid_until).toLocaleDateString()}
                </Typography>
                <a
                  href={deal.deal_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ marginTop: 10, display: 'block' }}
                >
                  Перейти к акции
                </a>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}

export default App;