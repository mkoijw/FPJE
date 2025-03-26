import torch
import pandas as pd
import torch.nn as nn
# 定义常量
MU_0 = 1e-7  # 真空磁导率 (N/A^2)
GRID_SIZE = 100  # 网格大小
num_ojz = 5000 # 偶极子数量

mag_file_name = 'SouthSea_1deg_1e4_MagMap.csv'
dipole_parameter_file_name = 'dipole_parameter.csv'
initial_dipole_pos_file_name = 'Initial_dipole_position.csv'
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 读取数据
df = pd.read_csv('data/' + mag_file_name, header=None)
df = torch.tensor(df.values, dtype=torch.float32)
obsPos = df[:, 3:6].to(device)
B_obs = df[:, 6:9].to(device)
B_obs = B_obs.view(GRID_SIZE, GRID_SIZE, 3).to(device)

# df = pd.read_csv(dipole_parameter_file_name)
# df = torch.tensor(df.values, dtype=torch.float32)
# magnetic_moments = df[:, 3:6].to(device)
# positions = df[:, 0:3].to(device)

# 初始化磁偶极子的位置和磁矩
df = pd.read_csv('data/' + initial_dipole_pos_file_name,header=None)
df = torch.tensor(df.values, dtype=torch.float32)
positions = df[:, 0:3].to(device)
positions = positions.clone().detach()
positions.requires_grad_(True)
magnetic_moments = torch.randn(num_ojz, 3, requires_grad=True) * 1e20
magnetic_moments = magnetic_moments.detach().clone()
magnetic_moments.requires_grad_(True)


def compute_magnetic_field(magnetic_moments, positions, obsPos):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    magnetic_moments = magnetic_moments.to(device)
    positions = positions.to(device)
    obsPos = obsPos.to(device)

    r_vec = obsPos.unsqueeze(0) - positions.unsqueeze(1)
    r = torch.norm(r_vec, dim=2, keepdim=True)

    r_dot_m = torch.sum(r_vec * magnetic_moments.unsqueeze(1), dim=2, keepdim=True)
    B = MU_0 * (3 * r_vec * r_dot_m / (r ** 5) - magnetic_moments.unsqueeze(1) / (
                r ** 3))

    B_total = B.sum(dim=0)

    B_total = B_total.view(GRID_SIZE, GRID_SIZE, 3)
    return B_total

optimizer = torch.optim.RMSprop([
    {'params': positions, 'lr': 100},
    {'params': magnetic_moments, 'lr': 1e27}
])

def loss_fn(B_total, target_B):
    return torch.norm(B_total - target_B)
loss_function = nn.MSELoss().to(device)

# 训练
for epoch in range(5000):
    optimizer.zero_grad()

    # 计算磁场
    B_total = compute_magnetic_field(magnetic_moments, positions, obsPos)

    # 计算损失
    loss = loss_function(B_total, B_obs)

    # 反向传播
    loss.backward()

    # 更新参数
    optimizer.step()

    print(f"Epoch {epoch}, Loss: {loss.item()}")

# 保存偶极子位置和磁矩为CSV
magnetic_moments_np = magnetic_moments.cpu().detach().numpy()
positions_np = positions.cpu().detach().numpy()
df_combined = pd.DataFrame({
    'Pos_x': positions_np[:, 0],
    'Pos_y': positions_np[:, 1],
    'Pos_z': positions_np[:, 2],
    'm_x': magnetic_moments_np[:, 0],
    'm_y': magnetic_moments_np[:, 1],
    'm_z': magnetic_moments_np[:, 2]
})
df_combined.to_csv('data/' + dipole_parameter_file_name, index=False)

