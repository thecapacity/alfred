drop table if exists links;
create table links (
      id integer primary key autoincrement,
      title text not null,
      url text not null,
      time text not null,
      tags text,
      comment text 
);
