use campuschefs_db;

-- Drop the tables in the correct order
drop table if exists comment;
drop table if exists likes;
drop table if exists images;
drop table if exists board;
drop table if exists ingredient;
drop table if exists post;
drop table if exists user;
drop table if exists test;

create table user (
    uid int auto_increment primary key,
    email_addr varchar(50),
    name varchar(30),
    school varchar(30),
    user_bio varchar(300),
    -- for logins and passwords
    -- password is hashed
    username varchar(50),
    password char(60),
    unique(username),
    index(username)
);

create table post (
    pid int auto_increment primary key,
    uid int,
    title varchar(1000), -- recipe title
    cover_photo blob,
    serving_size int,
    prep_time int, 
    cook_time int,
    like_count int,
    total_time int,
    post_date datetime,
    text_descrip varchar(1000),
    steps varchar(1000),
    tags set('vegan', 'vegetarian', 'gluten-free', 'dairy-free', 'nut-free', 'quick-meal', 'meal-prep', 'comfort-food', 'breakfast', 
                'brunch', 'lunch', 'dinner', 'dessert', 'snack', 'fall', 'spring', 'summer', 'winter'),
    price enum('low', 'medium', 'high'),
    foreign key (uid) references user(uid)
);

create table ingredient (
    pid int,
    FOREIGN KEY (pid) REFERENCES post(pid) ON DELETE CASCADE,
    name varchar(50),
    quantity int,
    measurement varchar(50)
);

create table images (
    image_id int auto_increment primary key,
    pid int,
    photo varchar(500),
    foreign key (pid) references post(pid)
);

create table likes (
    uid int,
    pid int,
    primary key (uid, pid),
    foreign key (uid) references user(uid),
    foreign key (pid) references post(pid) 
);

create table comment (
    comment_id int auto_increment primary key,
    uid int,
    pid int,
    content varchar(200),
    foreign key (uid) references user(uid),
    foreign key (pid) references post(pid) 
);

create table board (
    uid int,
    pid int,
    recipe enum('Made', 'To be made'),
    foreign key (uid) references user(uid),
    foreign key (pid) references post(pid) 
);