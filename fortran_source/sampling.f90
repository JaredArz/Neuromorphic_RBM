module sampling
    use MTJ_RNG_vars
    use ziggurat
    implicit none
    logical :: fwrite_enabled
    contains
        ! --------------------------------*------------*-----------------------------------
        !   energy_usage,bit,theta_end,phi_end, should not be passed into this function
        !   they are declared as they are because subroutine arguments declared with intent(out)
        !   will return back to python as a tuple (see numpy f2py)
        !
        !   intended to mimic the python function call: out,energy = dev.sample_*(Jappl,Jshe_in, self.theta, self.phi, self.Ki....)
        ! --------------------------------*------------*-----------------------------------
        subroutine sample_SHE(energy_usage, bit, theta_end, phi_end,&
                                 Jappl, Jshe, theta_init, phi_init, Ki_in, TMR_in, Rp_in,&
                                 dump_mod, view_mag_flag, sample_count, file_ID) 
            implicit none
            integer, parameter :: dp = kind(0.0d0)
            ! Dynamical parameters
            real, intent(in) :: Jappl, Jshe, theta_init, phi_init
            ! Device input parameters
            real, intent(in) :: Ki_in, TMR_in, Rp_in
            ! Functional parameters
            integer, intent(in) :: file_ID, dump_mod, sample_count
            logical, intent(in) :: view_mag_flag
            ! Return values
            real, intent(out) :: energy_usage, theta_end, phi_end
            integer, intent(out) :: bit
            !==================================================================
            real(dp), dimension(:), allocatable :: theta_evol, phi_evol
            real(dp) :: phi_i, theta_i, cuml_energy
            real :: seed
            integer :: t_i, pulse_steps, relax_steps, total_steps
            !==================================================================
            !//////////////////////////////////////////////////////////////////

            ! ======== solve init ========= 
            ! Fortran array indexing starts at 1
            t_i  = 1 
            fwrite_enabled = (mod(sample_count,dump_mod) .eq. 0 .and. view_mag_flag)

            pulse_steps = int(t_pulse/t_step)
            relax_steps = int(t_relax/t_step)
            total_steps = pulse_steps+relax_steps+1

            cuml_energy = 0.0_dp
            theta_i = real(theta_init, dp)
            phi_i   = real(phi_init, dp)
            if(fwrite_enabled) then
                allocate(theta_evol(total_steps))
                allocate(phi_evol(total_steps))
                theta_evol(t_i) = theta_i
                phi_evol(t_i)   = phi_i
            end if

            call set_params(Ki_in, TMR_in, Rp_in)

            call random_number(seed)
            call zigset(int(1+floor((1000001)*seed)))
            !================================

            !=========== Pulse current and set device to be in-plane =========
            call drive(0.0_dp, real(Jshe,dp), real(Jappl,dp), pulse_steps,&
                           t_i, phi_i, theta_i, phi_evol, theta_evol, cuml_energy)

            !=================  Relax into one of two low-energy states out-of-plane  ===================
            call drive(0.0_dp, 0.0_dp, real(Jappl,dp), relax_steps,&
                           t_i, phi_i, theta_i, phi_evol, theta_evol, cuml_energy)

            if(fwrite_enabled) then
                call file_dump(file_ID, phi_evol, theta_evol)
            end if

            ! ===== return final solve values: energy,bit,theta,phi ====
            if( cos(theta_i) > 0.0_dp ) then
                bit = 1
            else
                bit = 0
            end if
            ! Cast to real before returning to Python
            theta_end = real(theta_i)
            phi_end   = real(phi_i)
            energy_usage = real(cuml_energy)
            print *, energy_usage
        end subroutine sample_SHE

        subroutine drive(V, J_SHE, J_STT, steps, t_i, phi_i, theta_i, phi_evol, theta_evol, cuml_energy)
           implicit none
           integer,  parameter :: dp = kind(0.0d0)
           real(dp), intent(in) :: V, J_SHE, J_STT
           integer,  intent(in)  :: steps
           real(dp), dimension(:), intent(inout) :: phi_evol, theta_evol
           real(dp), intent(inout) :: phi_i, theta_i, cuml_energy
           integer,  intent(inout) :: t_i
           real(dp) :: Hk, Ax, Ay, Az, dphi, dtheta, R1, pow, cos_theta, sin_theta,&
                       cos_phi, sin_phi, v_pow, she_pow 
           integer  :: i

           Hk = (2.0_dp*Ki)/(tf*Ms*u0)-(2.0_dp*ksi*V)/(u0*Ms*tox*tf)
           v_pow = 0.5_dp*cap_mgo*V**2
           she_pow = R2*(J_SHE*A2)**2

           do i = 1, steps
               t_i = t_i+1
               cos_theta = cos(theta_i)
               sin_theta = sin(theta_i)
               cos_phi   = cos(phi_i)
               sin_phi   = sin(phi_i)
               Ax = Hx-Nx*Ms*sin_theta*cos_phi     +rnor()*Htherm
               Ay = Hy-Ny*Ms*sin_theta*sin_phi     +rnor()*Htherm
               Az = Hz-Nz*Ms*cos_theta+Hk*cos_theta+rnor()*Htherm

               dphi = gammap*(Ax*(-cos_theta*cos_phi - alpha*sin_phi) + Ay*(-cos_theta*sin_phi + alpha*cos_phi)&
                      + Az*sin_theta)/(sin_theta)+J_SHE*F*eta*(sin_phi-alpha*cos_phi*cos_theta)/(sin_theta&
                      * (1_dp+alpha**2)) - ((alpha*F*P*J_STT)/(1_dp+alpha**2))
               dtheta = gammap*(Ax*(alpha*cos_theta*cos_phi - sin_phi) + Ay*(alpha*cos_theta*sin_phi+cos_phi)&
                      - Az*alpha*sin_theta) - J_SHE*F*eta*(cos_phi*cos_theta + (alpha*sin_phi)/(1_dp+alpha**2))&
                      + ((F*P*J_STT)*sin_theta/(1_dp+alpha**2))
               ! only accounting for z-component
               R1 = Rp*(1_dp+(V/Vh)**2+TMR)/(1_dp+(V/Vh)**2 + TMR*(1_dp+cos_theta)/2_dp)

               pow = v_pow + she_pow + (R1*(J_STT*A1)**2)
               phi_i   = phi_i   + t_step*dphi 
               theta_i = theta_i + t_step*dtheta
               cuml_energy = cuml_energy + (pow * t_step)
               if(fwrite_enabled) then
                   theta_evol(t_i) = theta_i
                   phi_evol(t_i)   = phi_i
               end if
           end do
        end subroutine drive

        subroutine file_dump(file_ID, phi_evol, theta_evol)
            implicit none
            integer,  parameter :: dp = kind(0.0d0)
            real(dp), dimension(:), intent(in) :: phi_evol, theta_evol
            integer,  intent(in) :: file_ID
            character(len=7) :: file_string

            ! ===== array dump to file of theta/phi time evolution  ====
            write (file_string,'(I7.7)') file_ID
            open(unit = file_ID, file = "phi_time_evol_"//file_string//".txt", action = "write", status = "old",&
                    position="append",form = 'formatted')
            write(file_ID,'(ES24.17)',advance="no") phi_evol
            close(file_ID)

            write (file_string,'(I7.7)') file_ID
            open(unit = file_ID, file = "theta_time_evol_"//file_string//".txt", action = "write", status = "old",&
                    position="append",form = 'formatted')
            write(file_ID,'(ES24.17)',advance="no") theta_evol
            close(file_ID)
        end subroutine file_dump
end module sampling
