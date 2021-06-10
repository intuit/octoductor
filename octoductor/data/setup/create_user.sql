DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = '@user') THEN

      CREATE ROLE @user LOGIN ENCRYPTED PASSWORD '@password' NOCREATEDB;
   END IF;
END
$do$;
