
USE quiz_game;


/* =========================================================
   USERS TABLE
========================================================= */

CREATE TABLE IF NOT EXISTS users (

    id INT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(100) NOT NULL,

    email VARCHAR(150) NOT NULL UNIQUE,

    password VARCHAR(255) NOT NULL,

    reset_code VARCHAR(10) NULL,

    reset_expires DATETIME NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);



/* =========================================================
   ADMINS TABLE
========================================================= */

CREATE TABLE IF NOT EXISTS admins (

    id INT AUTO_INCREMENT PRIMARY KEY,

    username VARCHAR(100) NOT NULL UNIQUE,

    password VARCHAR(255) NOT NULL

);



/* =========================================================
   CHECK WHETHER results.user_id ALREADY EXISTS
========================================================= */

SET @column_exists := (

    SELECT COUNT(*)

    FROM information_schema.columns

    WHERE table_schema = DATABASE()

      AND table_name = 'results'

      AND column_name = 'user_id'

);



/* =========================================================
   ADD user_id ONLY IF IT DOES NOT EXIST
========================================================= */

SET @sql := IF(

    @column_exists = 0,

    'ALTER TABLE results ADD COLUMN user_id INT NULL AFTER id',

    'SELECT 1'

);


PREPARE stmt FROM @sql;

EXECUTE stmt;

DEALLOCATE PREPARE stmt;



/* =========================================================
   CHECK WHETHER FOREIGN KEY ALREADY EXISTS
========================================================= */

SET @fk_exists := (

    SELECT COUNT(*)

    FROM information_schema.table_constraints

    WHERE constraint_schema = DATABASE()

      AND table_name = 'results'

      AND constraint_name = 'fk_result_user'

      AND constraint_type = 'FOREIGN KEY'

);



/* =========================================================
   ADD FOREIGN KEY ONLY IF IT DOES NOT EXIST
========================================================= */

SET @sql := IF(

    @fk_exists = 0,

    'ALTER TABLE results ADD CONSTRAINT fk_result_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE',

    'SELECT 1'

);


PREPARE stmt FROM @sql;

EXECUTE stmt;

DEALLOCATE PREPARE stmt;

