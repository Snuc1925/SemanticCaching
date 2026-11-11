import { useCallback, useEffect, useState } from 'react';
import { api, Me, post } from '../../api';
import { COLLECTION_LABEL } from '../../components/ui';
import { Panel } from './Layout';

interface AdminUser { username: string; name: string; user_id: string; roles: string[]; attributes: Record<string, string>; collections_now: string[] }
interface Doc { doc_id: string; title: string; collection: string; versions: number[]; current_version: number | null }

export default function Admin({ me }: { me: Me }) {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [roles, setRoles] = useState<string[]>([]);
  const [docs, setDocs] = useState<Doc[]>([]);
  const [msg, setMsg] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    const u = await api<{ users: AdminUser[]; roles: string[] }>('/console/admin/users');
    setUsers(u.users); setRoles(u.roles);
    setDocs(await api<Doc[]>('/console/admin/documents'));
  }, []);
  useEffect(() => { load().catch((e) => setMsg(e.message)); }, [load]);

  async function run(label: string, fn: () => Promise<unknown>) {
    setBusy(true); setMsg(null);
    try { await fn(); setMsg(label); await load(); } catch (e: any) { setMsg(`Không thực hiện được: ${e.message}`); } finally { setBusy(false); }
  }

  const toggle = (u: AdminUser, role: string) => {
    const grant = !u.roles.includes(role);
    return run(`${grant ? 'Đã cấp' : 'Đã thu hồi'} vai trò ${role} ${grant ? 'cho' : 'của'} ${u.username}. Hệ thống áp dụng sau vài giây (xem trang Bảo mật).`,
      () => post(`/console/admin/users/${u.username}/roles`, { role, grant }));
  };

  return (
    <div className="grid gap-4">
      {msg && <div className="glass rounded-2xl px-4 py-3 text-sm" role="status" data-testid="admin-message">{msg}</div>}
      <Panel title="Người dùng và vai trò" actions={
        <button className="pill" disabled={busy} data-testid="reset-demo"
          onClick={() => run('Đã khôi phục dữ liệu demo về trạng thái ban đầu.', () => post('/console/admin/reset', { clear_history: false }))}>
          Khôi phục dữ liệu demo
        </button>}>
        <p className="faint text-xs mb-3">Bấm vào một vai trò để cấp hoặc thu hồi. Thay đổi được ghi vào Keycloak giống như quản trị viên đổi quyền trực tiếp.</p>
        <div className="overflow-x-auto">
          <table className="data" data-testid="admin-users">
            <thead><tr><th>Người dùng</th><th>Vai trò</th><th>Thuộc tính</th><th>Đọc được (theo IAM, ngay lúc này)</th></tr></thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.username} data-testid={`user-${u.username}`}>
                  <td><div className="font-medium">{u.name}</div><div className="faint text-xs">{u.username}</div></td>
                  <td>
                    <div className="flex flex-wrap gap-1">
                      {roles.map((r) => {
                        const on = u.roles.includes(r);
                        const locked = u.username === me.username && r === 'ops_admin';
                        return (
                          <button key={r} disabled={busy || locked} onClick={() => toggle(u, r)} aria-pressed={on}
                            data-testid={`role-${u.username}-${r}`}
                            className={`pill !py-1 !px-3 text-xs ${on ? 'pill-primary' : 'faint'}`}
                            title={locked ? 'Không tự thu hồi quyền Console của chính mình' : on ? 'Bấm để thu hồi' : 'Bấm để cấp'}>
                            {r}
                          </button>
                        );
                      })}
                    </div>
                  </td>
                  <td className="muted">{Object.entries(u.attributes).map(([k, v]) => `${k}=${v}`).join(', ') || '–'}</td>
                  <td>{u.collections_now.map((c) => COLLECTION_LABEL[c] ?? c).join(', ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      <Panel title="Tài liệu">
        <p className="faint text-xs mb-3">Xuất bản version khác sẽ nạp lại tài liệu và xoá các câu trả lời trong cache được sinh từ tài liệu đó.</p>
        <table className="data" data-testid="admin-docs">
          <thead><tr><th>Tài liệu</th><th>Collection</th><th>Version hiện tại</th><th></th></tr></thead>
          <tbody>
            {docs.map((d) => (
              <tr key={d.doc_id}>
                <td><div className="font-medium">{d.title}</div><div className="faint text-xs">{d.doc_id}</div></td>
                <td>{COLLECTION_LABEL[d.collection] ?? d.collection}</td>
                <td>v{d.current_version}</td>
                <td className="text-right">
                  {d.versions.filter((v) => v !== d.current_version).map((v) => (
                    <button key={v} className="pill !py-1 text-sm" disabled={busy} data-testid={`publish-${d.doc_id}-v${v}`}
                      onClick={() => run(`Đã xuất bản ${d.doc_id} v${v}.`, () => post(`/console/admin/documents/${d.doc_id}/publish`, { version: v }))}>
                      Xuất bản v{v}
                    </button>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Panel>
    </div>
  );
}
