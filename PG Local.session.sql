SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

SELECT * FROM poll_responses;

SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'poll_responses'; 

