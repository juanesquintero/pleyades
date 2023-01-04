-- **********************************
-- ******** Database & User *********
-- **********************************
CREATE SCHEMA `pleyades` DEFAULT CHARACTER SET latin1 ;

CREATE USER 'pleyades'@'%' IDENTIFIED BY ''; 

GRANT ALL PRIVILEGES ON pleyades.* TO 'pleyades'@'%';