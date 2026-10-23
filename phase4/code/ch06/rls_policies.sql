-- =============================================================================
-- LessonVault · 最小 RLS 基线（PostgreSQL / Supabase 语法）
-- 用途：第 01 章 3.4 节的示范。可整段在 Supabase SQL Editor 里执行。
-- 核心主张：访问控制必须落在「数据层」，不能落在「前端只查自己的数据」上。
-- =============================================================================

-- 0) 最小表结构 ---------------------------------------------------------------
create table if not exists public.profiles (
    id          uuid primary key references auth.users (id) on delete cascade,
    email       text,
    created_at  timestamptz not null default now()
);

create table if not exists public.notes (
    id          bigint generated always as identity primary key,
    owner_id    uuid not null references auth.users (id) on delete cascade,
    title       text not null,
    body        text,
    created_at  timestamptz not null default now()
);

create index if not exists notes_owner_idx on public.notes (owner_id);

-- 1) 打开 RLS —— 这一步是「总闸」。没有它，下面所有 policy 都不生效。
alter table public.profiles enable row level security;
alter table public.notes    enable row level security;

-- 2) 按「动作」分别授权，不要用一条 all 覆盖四种语义 -------------------------
--    select / update 用 using（读的时候看哪一行可见）
--    insert 用 with check（写的时候看新行长什么样）
--    update 两个都要给：using 决定改哪一行，with check 决定改成什么样
drop policy if exists notes_select_own on public.notes;
create policy notes_select_own on public.notes
    for select to authenticated
    using (owner_id = auth.uid());

drop policy if exists notes_insert_own on public.notes;
create policy notes_insert_own on public.notes
    for insert to authenticated
    with check (owner_id = auth.uid());

drop policy if exists notes_update_own on public.notes;
create policy notes_update_own on public.notes
    for update to authenticated
    using (owner_id = auth.uid())
    with check (owner_id = auth.uid());

drop policy if exists notes_delete_own on public.notes;
create policy notes_delete_own on public.notes
    for delete to authenticated
    using (owner_id = auth.uid());

-- 3) profiles：只允许读自己那一行，且不允许改 email（改邮箱走服务端）
drop policy if exists profiles_select_own on public.profiles;
create policy profiles_select_own on public.profiles
    for select to authenticated
    using (id = auth.uid());

-- 4) 反面教材（不要照抄）----------------------------------------------------
--    using (true) 等于「对所有登录用户开放全表」，写了 policy 反而是最危险的：
--    你会以为已经设防了。
--
--    create policy notes_all_open on public.notes
--        for all to authenticated using (true) with check (true);

-- =============================================================================
-- 5) 自测：这三条必须在「匿名 / 他人身份」下失败
--    在 Supabase SQL Editor 里，用 set local role 切换角色来验证。
--    注意：SQL Editor 默认以 postgres（超级用户）身份运行，会绕过 RLS，
--    所以必须显式切角色，否则你永远测出「通过」。
-- =============================================================================
-- set local role anon;
-- select count(*) from public.notes;          -- 期望：0（或直接 permission denied）
-- reset role;
--
-- set local role authenticated;
-- set local request.jwt.claims = '{"sub":"<用户A的uuid>","role":"authenticated"}';
-- select count(*) from public.notes;          -- 期望：只等于用户A自己的行数
-- reset role;

-- =============================================================================
-- 6) 一个容易漏掉的第二现场：Storage
--    notes 表设了 RLS，附件桶没设，等于前门上锁、后窗开着。
--    Supabase Storage 的 objects 表同样受 RLS 约束，策略形状与上面一致：
--    路径第一段放 owner_id，用 (storage.foldername(name))[1] = auth.uid()::text 判定。
-- =============================================================================
-- drop policy if exists notes_files_owner_only on storage.objects;
-- create policy notes_files_owner_only on storage.objects
--     for all to authenticated
--     using (
--         bucket_id = 'notes-files'
--         and (storage.foldername(name))[1] = auth.uid()::text
--     )
--     with check (
--         bucket_id = 'notes-files'
--         and (storage.foldername(name))[1] = auth.uid()::text
--     );
