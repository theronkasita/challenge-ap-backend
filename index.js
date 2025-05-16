const express = require('express');
const cors = require('cors');
const pool = require('./db');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

// GET total registrations
app.get('/api/total-registrations', async (req, res) => {
  try {
    const result = await pool.query('SELECT COUNT(*) as total FROM students');
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET registrations by programme with optional academic year filter
app.get('/api/registrations-by-programme', async (req, res) => {
  try {
    const { year } = req.query;
    let query = `
      SELECT study_programme, COUNT(*) as count
      FROM students
    `;
    const params = [];

    if (year && year !== 'all') {
      query += ` WHERE academic_year = $1 `;
      params.push(year);
    }

    query += `
      GROUP BY study_programme
      ORDER BY count DESC
    `;

    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET registrations by school
app.get('/api/registrations-by-school', async (req, res) => {
  try {
    const query = `
      SELECT secondary_school, COUNT(*) as count
      FROM students
      GROUP BY secondary_school
      ORDER BY count DESC
    `;
    const result = await pool.query(query);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET registrations by academic year with optional programme filter
app.get('/api/registrations-by-year', async (req, res) => {
  try {
    const { programme } = req.query;
    let query = `
      SELECT academic_year, COUNT(*) as count
      FROM students
    `;
    const params = [];

    if (programme && programme !== 'all') {
      query += ` WHERE study_programme = $1 `;
      params.push(programme);
    }

    query += `
      GROUP BY academic_year
      ORDER BY academic_year
    `;

    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET top 10 schools by registrations
app.get('/api/top-schools', async (req, res) => {
  try {
    const query = `
      SELECT secondary_school, COUNT(*) as count
      FROM students
      GROUP BY secondary_school
      ORDER BY count DESC
      LIMIT 10
    `;
    const result = await pool.query(query);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

const port = process.env.PORT || 5000;
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
