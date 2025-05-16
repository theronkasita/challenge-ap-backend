const fs = require('fs');
const { Pool } = require('pg');

const pool = new Pool({
  user: 'postgres',
  host: 'localhost',
  database: 'studentdb',
  password: 'admin',
  port: 5008
});

const data = JSON.parse(fs.readFileSync('mock_student_data.json', 'utf8'));

const formatDate = (input) => {
  const [month, day, year] = input.split('/');
  return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
};

const insertData = async () => {
  try {
    for (const student of data) {
      const formattedDate = formatDate(student.registration_date);
      await pool.query(
        `INSERT INTO students (
          id, first_name, last_name, email, gender, student_id,
          study_programme, secondary_school, registration_date, academic_year
        ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)`,
        [
          student.id,
          student.first_name,
          student.last_name,
          student.email,
          student.gender,
          student.student_id,
          student.study_programme,
          student.secondary_school,
          formattedDate,
          student.academic_year
        ]
      );
    }
    console.log("✅ Students imported successfully!");
  } catch (err) {
    console.error("❌ Error inserting data:", err);
  } finally {
    await pool.end();
  }
};

insertData();
