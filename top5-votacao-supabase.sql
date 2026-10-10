-- Top 5 Latino voting backend. Run once in the Supabase SQL editor.
-- Vote rows are private; visitors only call the two restricted functions.
create table if not exists public.top5_votes (
  edition text not null,
  song_id text not null,
  visitor uuid not null,
  created_at timestamptz not null default now(),
  primary key (edition, visitor)
);
alter table public.top5_votes enable row level security;
revoke all on public.top5_votes from anon, authenticated;
create or replace function public.top5_get_counts(p_edition text)
returns table (song_id text, votes bigint)
language sql security definer set search_path = public
as $$
 select v.song_id, count(*)::bigint from public.top5_votes v
 where v.edition=p_edition group by v.song_id;
$$;
create or replace function public.top5_cast_vote(p_edition text,p_song_id text,p_visitor uuid)
returns jsonb
language plpgsql security definer set search_path = public
as $$
begin
 if length(p_edition) not between 15 and 240 or length(p_song_id) not between 4 and 40 then
   raise exception 'Invalid vote';
 end if;
 insert into public.top5_votes(edition,song_id,visitor)
 values(p_edition,p_song_id,p_visitor)
 on conflict (edition,visitor) do nothing;
 if not found then
   raise exception 'Already voted in this edition';
 end if;
 return jsonb_build_object('ok',true);
end;
$$;
revoke all on function public.top5_get_counts(text) from public;
revoke all on function public.top5_cast_vote(text,text,uuid) from public;
grant execute on function public.top5_get_counts(text) to anon,authenticated;
grant execute on function public.top5_cast_vote(text,text,uuid) to anon,authenticated;
-- Limitations: visitor UUID stored in the browser is not strong identity;
-- a determined user can evade one-vote-per-browser restrictions. 
