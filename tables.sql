use campuschefs_db;

-- Drop the tables in the correct order
drop table if exists post;
drop table if exists images;
drop table if exists user;

create table user (
    uid int auto_increment primary key,
    email_addr varchar(50),
    name varchar(30),
    school varchar(30),
    user_bio varchar(300)
);

create table follow (
    uid_1 int,
    foreign key (uid_1) references user(uid),
    uid_2 int,
    foreign key (uid_2) references user(uid)
);

create table post (
    pid int auto_increment primary key,
    uid int,
    cover_photo blob,
    text_descrip varchar(1000),
    tags enum('spicy', 'dessert', 'breakfast', 'dinner', 'lunch'),
    price enum('$', '$$', '$$$'),
    foreign key (uid) references user(uid)
);

create table images (
    image_id int auto_increment primary key,
    pid int,
    photo blob,
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

create table conversation (
    conver_id int auto_increment primary key,
    og_comment_id int,
    reply_id int,
    foreign key (og_comment_id) references comment(comment_id),
    foreign key (reply_id) references comment(comment_id)
);

create table board (
    uid int,
    pid int,
    recipe enum('Made', 'To be made'),
    foreign key (uid) references user(uid),
    foreign key (pid) references post(pid)
);
