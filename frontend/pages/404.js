import * as React from 'react';
import { Box, Typography } from '@mui/material';

export default function Custom404() {
  return (
    <Box sx={{ textAlign: 'center', mt: 8 }}>
      <Typography variant="h3" color="primary" gutterBottom>
        404 – Page Not Found
      </Typography>
      <Typography variant="body1">The page you are looking for does not exist.</Typography>
    </Box>
  );
}
