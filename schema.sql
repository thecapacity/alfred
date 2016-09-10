drop table if exists links;
create table links (
      id integer primary key autoincrement,
      private int not null default 0,
      title text not null,
      url text not null,
      time text not null,
      tags text,
      comment text,
      json_blob text 
);
