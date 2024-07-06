
create table if not exists users (
    id varchar(36) NOT NULL CONSTRAINT user_pkey PRIMARY KEY,
    account varchar(255) UNIQUE,
    email_address varchar(255) UNIQUE,
    hashed_password varchar,
    authority varchar(255),
    additional_info varchar
);

COMMENT ON COLUMN users.id IS '流水號';
COMMENT ON COLUMN users.account IS '帳號';
COMMENT ON COLUMN users.email_address IS '電子郵件';
COMMENT ON COLUMN users.hashed_password IS '密碼';
COMMENT ON COLUMN users.authority IS '權限';
COMMENT ON COLUMN users.additional_info IS '其他資訊';