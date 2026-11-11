# 06_revoke: Console: admin_ops thu hồi role cskh_agent của cskh1 → Keycloak admin event → poller

47 lời gọi hàm.

```text
▶ auth.current_user   [1.3 ms]   (thread: AnyIO worker thread, dòng 35)
│    in  request = <Request>
│  ▶ auth.decode   [1.1 ms]   (thread: AnyIO worker thread, dòng 23)
│  │    in  token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiZGU1ODRiZGQtOTA3OS00NTQ1LTkwZWQtZmE1MGNjYjAyNzA3Iiwi…(+1219 ký tự)'
│  │    out = UserContext(user_id='5b7a9394-f2ca-44a8-acb5-37953e298ad1', username='admin_ops', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'ops_admin', 'employee'), display_name='Quản trị vận hành')
│    out = UserContext(user_id='5b7a9394-f2ca-44a8-acb5-37953e298ad1', username='admin_ops', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'ops_admin', 'employee'), display_name='Quản trị vận hành')

▶ auth.console_user   [0.0 ms]   (thread: AnyIO worker thread, dòng 42)
│    in  user = UserContext(user_id='5b7a9394-f2ca-44a8-acb5-37953e298ad1', username='admin_ops', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'ops_admin', 'employee'), display_name='Quản trị vận hành')
│    out = UserContext(user_id='5b7a9394-f2ca-44a8-acb5-37953e298ad1', username='admin_ops', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'ops_admin', 'employee'), display_name='Quản trị vận hành')

▶ main.admin_set_role   [104.0 ms]   (thread: AnyIO worker thread, dòng 236)
│    in  username = 'cskh1'
│    in  body = RoleIn({role: 'cskh_agent', grant: False})
│    in  actor = UserContext(user_id='5b7a9394-f2ca-44a8-acb5-37953e298ad1', username='admin_ops', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'ops_admin', 'employee'), display_name='Quản trị vận hành')
│  ▶ main._acl   [41.8 ms]   (thread: AnyIO worker thread, dòng 207)
│  │    out = {realm: 'semcache', roles: [{name: 'customer', description: 'Khách hàng'}, {name: 'employee', description: 'Nhân viên (mọi phòng ban)'}, {name: 'cskh_agent', description: 'Nhân viên chăm sóc khách hàng'}, {name: 'hr', description: 'Nhân sự'}, {name: 'sales', description: 'Kinh doanh / đại lý'}, {name: 'ops_admin', description: 'Vận hành hệ thống, được vào Console'}], policies: [{name: 'p_any_user', type: 'role', roles: <list>}, {name: 'p_employee', type: 'role', roles: <list>}, {name: 'p_cskh', type: 'role', roles: <list>}, {name: 'p_hr', type: 'role', roles: <list>}, {name: 'p_sales', type: 'role', roles: <list>}, {name: 'p_region_north', type: 'regex', claim: 'region', pattern: '^north$'}, …(+1)], collections: {public: {title: 'Tài liệu công khai', policies: <list>}, internal_all: {title: 'Tài liệu nội bộ chung', policies: <list>}, cskh: {title: 'Tài liệu nội bộ CSKH', policies: <list>}, hr_confidential: {title: 'Nhân sự - mật', policies: <list>}, sales_north: {title: 'Kinh doanh miền Bắc', policies: <list>}, sales_south: {title: 'Kinh doanh miền Nam', policies: <list>}}, default_password: 'demo1234', users: [{username: 'khach', name: 'Khách Hàng', roles: <list>}, {username: 'cskh1', name: 'Lan CSKH', roles: <list>}, {username: 'cskh2', name: 'Minh CSKH', roles: <list>}, {username: 'sales_bac', name: 'Hùng Sales Bắc', roles: <list>, attributes: <dict>}, {username: 'sales_nam', name: 'Vy Sales Nam', roles: <list>, attributes: <dict>}, {username: 'hr1', name: 'Hà Nhân Sự', roles: <list>}, …(+1)]}
│  ▶ iam.keycloak.KeycloakAdmin.find_user   [13.5 ms]   (thread: AnyIO worker thread, dòng 65)
│  │    in  username = 'cskh1'
│  │  ▶ iam.keycloak.KeycloakAdmin.request   [13.3 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │    in  method = 'GET'
│  │  │    in  path = '/users'
│  │  │    in  kw = {params: {username: 'cskh1', exact: 'true'}}
│  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/users?username=cskh1&exact=true>
│  │    out = {id: '829671b9-5f8b-431d-9b2f-8a31158a3a2d', username: 'cskh1', firstName: 'Lan', lastName: 'CSKH', email: 'cskh1@saomai.local', emailVerified: True, createdTimestamp: 1794339204584, enabled: True, totp: False, disableableCredentialTypes: [], …(+3 khoá)}
│  ▶ iam.keycloak.KeycloakAdmin.set_realm_role   [48.4 ms]   (thread: AnyIO worker thread, dòng 78)
│  │    in  user_id = '829671b9-5f8b-431d-9b2f-8a31158a3a2d'
│  │    in  role = 'cskh_agent'
│  │    in  grant = False
│  │  ▶ iam.keycloak.KeycloakAdmin.realm_role   [7.6 ms]   (thread: AnyIO worker thread, dòng 75)
│  │  │    in  name = 'cskh_agent'
│  │  │  ▶ iam.keycloak.KeycloakAdmin.request   [7.5 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │  │    in  method = 'GET'
│  │  │  │    in  path = '/roles/cskh_agent'
│  │  │  │    in  kw = {}
│  │  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/roles/cskh_agent>
│  │  │    out = {id: 'fce33e7e-8385-4b19-a094-2f378867ecfb', name: 'cskh_agent', description: 'Nhân viên chăm sóc khách hàng', composite: False, clientRole: False, containerId: '36a24d23-b72a-438a-a29d-ea82714c2772', attributes: {}}
│  │  ▶ iam.keycloak.KeycloakAdmin.request   [40.7 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │    in  method = 'DELETE'
│  │  │    in  path = '/users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm'
│  │  │    in  kw = {json: [{id: 'fce33e7e-8385-4b19-a094-2f378867ecfb', name: 'cskh_agent'}]}
│  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │    out = <HTTP 204 http://localhost:8080/admin/realms/semcache/users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm>
│  │    out = None
│    out = {ok: True, username: 'cskh1', role: 'cskh_agent', grant: False}

▶ sync.PermissionSync.poll_once   [56.1 ms]   (thread: permission-sync, dòng 66)
│  ▶ iam.keycloak.KeycloakEventSource.poll   [21.8 ms]   (thread: permission-sync, dòng 156)
│  │  ▶ iam.keycloak.KeycloakAdmin.admin_events   [21.4 ms]   (thread: permission-sync, dòng 112)
│  │  │    in  max_results = 200
│  │  │  ▶ iam.keycloak.KeycloakAdmin.request   [20.8 ms]   (thread: permission-sync, dòng 52)
│  │  │  │    in  method = 'GET'
│  │  │  │    in  path = '/admin-events'
│  │  │  │    in  kw = {params: {max: 200}}
│  │  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: permission-sync, dòng 39)
│  │  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMjM3NDlhMGQtMGYxNC00NGI0LThlNjQtODZiODliZGQ5YzZhIiwi…(+1419 ký tự)'
│  │  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/admin-events?max=200>
│  │  │    out = [{time: 1794371861745, realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', authDetails: {realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', clientId: 'b241a711-46be-488a-b226-d122149c1b86', userId: '4e121ac4-b49f-48e7-8758-ebbbda82b3a5', ipAddress: '172.30.0.1'}, operationType: 'DELETE', resourceType: 'REALM_ROLE_MAPPING', resourcePath: 'users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm', representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]'}, {time: 1794370061899, realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', authDetails: {realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', clientId: 'b241a711-46be-488a-b226-d122149c1b86', userId: '4e121ac4-b49f-48e7-8758-ebbbda82b3a5', ipAddress: '172.30.0.1'}, operationType: 'CREATE', resourceType: 'REALM_ROLE_MAPPING', resourcePath: 'users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm', representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]'}, {time: 1794370051386, realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', authDetails: {realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', clientId: 'b241a711-46be-488a-b226-d122149c1b86', userId: '4e121ac4-b49f-48e7-8758-ebbbda82b3a5', ipAddress: '172.30.0.1'}, operationType: 'DELETE', resourceType: 'REALM_ROLE_MAPPING', resourcePath: 'users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm', representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]'}, {time: 1794369953009, realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', authDetails: {realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', clientId: 'b241a711-46be-488a-b226-d122149c1b86', userId: '4e121ac4-b49f-48e7-8758-ebbbda82b3a5', ipAddress: '172.30.0.1'}, operationType: 'CREATE', resourceType: 'REALM_ROLE_MAPPING', resourcePath: 'users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm', representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]'}, {time: 1794369939412, realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', authDetails: {realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', clientId: 'b241a711-46be-488a-b226-d122149c1b86', userId: '4e121ac4-b49f-48e7-8758-ebbbda82b3a5', ipAddress: '172.30.0.1'}, operationType: 'DELETE', resourceType: 'REALM_ROLE_MAPPING', resourcePath: 'users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm', representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]'}, {time: 1794339261520, realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', authDetails: {realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', clientId: 'b241a711-46be-488a-b226-d122149c1b86', userId: '4e121ac4-b49f-48e7-8758-ebbbda82b3a5', ipAddress: '172.30.0.6'}, operationType: 'CREATE', resourceType: 'REALM_ROLE_MAPPING', resourcePath: 'users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm', representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]'}, …(+49)]
│  │  ▶ iam.keycloak._event_key   [0.0 ms]   (thread: permission-sync, dòng 142)
│  │  │    in  e = {time: 1794371861745, realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', authDetails: {realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', clientId: 'b241a711-46be-488a-b226-d122149c1b86', userId: '4e121ac4-b49f-48e7-8758-ebbbda82b3a5', ipAddress: '172.30.0.1'}, operationType: 'DELETE', resourceType: 'REALM_ROLE_MAPPING', resourcePath: 'users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm', representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]'}
│  │  │    out = '1794371861745|DELETE|REALM_ROLE_MAPPING|users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm|35052e3dac'
│  │  ▶ iam.keycloak._event_key   [0.0 ms]   (thread: permission-sync, dòng 142)
│  │  │    in  e = {time: 1794371861745, realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', authDetails: {realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', clientId: 'b241a711-46be-488a-b226-d122149c1b86', userId: '4e121ac4-b49f-48e7-8758-ebbbda82b3a5', ipAddress: '172.30.0.1'}, operationType: 'DELETE', resourceType: 'REALM_ROLE_MAPPING', resourcePath: 'users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm', representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]'}
│  │  │    out = '1794371861745|DELETE|REALM_ROLE_MAPPING|users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm|35052e3dac'
│  │    out = [AccessChangeEvent(occurred_at=<datetime>, kind='role_mapping', summary='DELETE REALM_ROLE_MAPPING (users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm)', user_ids=['829671b9-5f8b-431d-9b2f-8a31158a3a2d'], affects_all=False, raw={time: 1794371861745, realmId: '36a24d23-b72a-438a-a29d-ea82714c2772', authDetails: <dict>, operationType: 'DELETE', resourceType: 'REALM_ROLE_MAPPING', resourcePath: 'users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm', representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]'})]
│  ▶ sync._now   [0.0 ms]   (thread: permission-sync, dòng 23)
│  │    out = <datetime>
│  ▶ access.invalidate   [2.3 ms]   (thread: permission-sync, dòng 62)
│  │    in  user_id = '829671b9-5f8b-431d-9b2f-8a31158a3a2d'
│  │    out = True
│  ▶ iam.keycloak.KeycloakAdmin.request   [25.9 ms]   (thread: permission-sync, dòng 52)
│  │    in  method = 'GET'
│  │    in  path = '/users/829671b9-5f8b-431d-9b2f-8a31158a3a2d'
│  │    in  kw = {}
│  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: permission-sync, dòng 39)
│  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMjM3NDlhMGQtMGYxNC00NGI0LThlNjQtODZiODliZGQ5YzZhIiwi…(+1419 ký tự)'
│  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/users/829671b9-5f8b-431d-9b2f-8a31158a3a2d>
│  ▶ sync._now   [0.0 ms]   (thread: permission-sync, dòng 23)
│  │    out = <datetime>
│  ▶ sync.record_event   [5.7 ms]   (thread: permission-sync, dòng 27)
│  │    in  kind = 'permission_change'
│  │    in  source = 'keycloak'
│  │    in  occurred_at = <datetime>
│  │    in  detected_at = <datetime>
│  │    in  effective_at = <datetime>
│  │    in  summary = 'DELETE REALM_ROLE_MAPPING (users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm) -> tính lại signature: cskh1'
│  │    in  details = {kind: 'role_mapping', user_ids: ['829671b9-5f8b-431d-9b2f-8a31158a3a2d'], usernames: ['cskh1'], signatures_invalidated: 1, operation: 'DELETE', representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]'}
│  │  ▶ db.fetch_one   [4.8 ms]   (thread: permission-sync, dòng 104)
│  │  │    in  sql = 'INSERT INTO security_events(kind,source,occurred_at,detected_at,effective_at,summary,details)⏎           VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING *'
│  │  │    in  params = ('permission_change', 'keycloak', <datetime>, <datetime>, <datetime>, 'DELETE REALM_ROLE_MAPPING (users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm) -> tính lại signature: cskh1', …(+1))
│  │  │    out = {id: 22, kind: 'permission_change', source: 'keycloak', occurred_at: <datetime>, detected_at: <datetime>, effective_at: <datetime>, summary: 'DELETE REALM_ROLE_MAPPING (users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm) -> tính lại signature: cskh1', details: {kind: 'role_mapping', user_ids: ['829671b9-5f8b-431d-9b2f-8a31158a3a2d'], operation: 'DELETE', usernames: ['cskh1'], representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]', signatures_invalidated: 1}}
│  │  ▶ tracing.publish   [0.7 ms]   (thread: permission-sync, dòng 85)
│  │  │    in  kind = 'security'
│  │  │    in  data = {id: 22, kind: 'permission_change', source: 'keycloak', occurred_at: '2026-11-11T04:37:41.745000+00:00', detected_at: '2026-11-11T04:37:41.870108+00:00', effective_at: '2026-11-11T04:37:41.898522+00:00', summary: 'DELETE REALM_ROLE_MAPPING (users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm) -> tính lại signature: cskh1', details: {kind: 'role_mapping', user_ids: ['829671b9-5f8b-431d-9b2f-8a31158a3a2d'], operation: 'DELETE', usernames: ['cskh1'], representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]', signatures_invalidated: 1}}
│  │  │    out = None
│  │    out = {id: 22, kind: 'permission_change', source: 'keycloak', occurred_at: '2026-11-11T04:37:41.745000+00:00', detected_at: '2026-11-11T04:37:41.870108+00:00', effective_at: '2026-11-11T04:37:41.898522+00:00', summary: 'DELETE REALM_ROLE_MAPPING (users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm) -> tính lại signature: cskh1', details: {kind: 'role_mapping', user_ids: ['829671b9-5f8b-431d-9b2f-8a31158a3a2d'], operation: 'DELETE', usernames: ['cskh1'], representation: '[{"id":"fce33e7e-8385-4b19-a094-2f378867ecfb","name":"cskh_agent","composite":false}]', signatures_invalidated: 1}}
│    out = 1

```
