import urllib.request
import urllib.parse
import json
import sys

BASE = 'http://localhost:8080/api'

def req(method, path, data=None, token=None):
    url = BASE + path
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    body = None
    if data is not None:
        body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp_body = resp.read()
            try:
                return resp.getcode(), json.loads(resp_body.decode())
            except Exception:
                return resp.getcode(), resp_body.decode()
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, e.reason
    except Exception as e:
        return None, str(e)

if __name__ == '__main__':
    print('Login...')
    status, data = req('POST', '/login', {'username':'admin','password':'admin123'})
    print('LOGIN', status, data)
    if status != 200:
        print('Login failed, aborting')
        sys.exit(1)
    token = data.get('token')

    print('\nGET /employees')
    print(req('GET', '/employees', token=token))

    print('\nPOST /employees')
    emp = {'name':'Smoke Test User','category':'Helper','email':'smoke@local','phone':'+100','status':'active'}
    print(req('POST', '/employees', emp, token))

    print('\nGET /employees (after add)')
    status, employees = req('GET', '/employees', token=token)
    print(status, isinstance(employees, dict) and len(employees.get('employees', [])) or employees)

    new_id = None
    if isinstance(employees, dict) and employees.get('employees'):
        # find added by name
        for e in employees['employees']:
            if e.get('name') == 'Smoke Test User':
                new_id = e.get('id')
                break

    if new_id:
        print('\nPUT /employees/{id}')
        upd = {'name':'Smoke User Updated','category':'Helper','email':'smoke2@local','phone':'+101','status':'active'}
        print(req('PUT', f'/employees/{new_id}', upd, token))

        print('\nDELETE /employees/{id}')
        print(req('DELETE', f'/employees/{new_id}', token=token))
    else:
        print('Could not find created employee to update/delete')

    print('\nPOST /allocations')
    rows = [{'process':'Smoke Process','category':'Helper','plan':1,'assigned':'','status':'pending'}]
    alloc = {'cellId':'1','date':urllib.parse.quote_plus(__import__('datetime').date.today().isoformat()),'shift':1,'rows':rows}
    # date was URL-encoded; server expects plain date in JSON, fix:
    alloc['date'] = __import__('datetime').date.today().isoformat()
    print(req('POST', '/allocations', alloc, token))

    print('\nGET /allocations')
    qs = urllib.parse.urlencode({'cellId':'1','date': __import__('datetime').date.today().isoformat()})
    print(req('GET', f'/allocations?{qs}', token=token))

    print('\nGET /allocations/history')
    qs = urllib.parse.urlencode({'date': __import__('datetime').date.today().isoformat(), 'cellId':'1'})
    print(req('GET', f'/allocations/history?{qs}', token=token))

    print('\nGET /analytics')
    print(req('GET', '/analytics', token=token))
