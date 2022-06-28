package com.dchealth.entity.common;


import org.hibernate.annotations.GenericGenerator;

import javax.persistence.*;
import java.sql.Timestamp;
import java.util.Date;

/**
 * Created by Administrator on 2017/6/5.
 */
@Entity
@Table(name = "yun_users", schema = "emhbase", catalog = "")
public class YunUsers  {
    private String id;
    private String userName;
    private String userId;
    private String loginFlags;
    private String deptId;
    private String sex;
  	private String homeAddress;
    private String nation;
    private String mobile;
    private String tel;
    private String email;
    private Timestamp birthDate;
    private Timestamp createDate;
    private Timestamp modifyDate;
    private String practiceQualificationId;
    private String extkey;
    private String title;
    private String researchDirection;
    private String signature;
    private String picture;
    private String rolename;
    private String salt ;
    private String password ;
    private String hospitalName;
    private String hospitalCode ;
    private String status;
    private String certificatePracticeId;
    private String qualificationCertificateId;
    private String newField1;
    private String newField2;
    private String newField3;
    private String newField4;
    private String newField5;
    private String newField6;
  	private String shmiglibob52;
    @Basic
    @Column(name = "certificate_practice_id")
    public String getCertificatePracticeId() {
        return certificatePracticeId;
    }

    public void setCertificatePracticeId(String certificatePracticeId) {
        this.certificatePracticeId = certificatePracticeId;
    }
    @Basic
    @Column(name = "qualification_certificate_id")
    public String getQualificationCertificateId() {
        return qualificationCertificateId;
    }

    public void setQualificationCertificateId(String qualificationCertificateId) {
        this.qualificationCertificateId = qualificationCertificateId;
    }

    @Id
    @Column(name = "id")
    @GenericGenerator(name="generator",strategy = "uuid.hex")
    @GeneratedValue(generator = "generator")
    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    @Basic
    @Column(name = "user_name")
    public String getUserName() {
        return userName;
    }

    public void setUserName(String userName) {
        this.userName = userName;
    }

    @Basic
    @Column(name = "user_id")
    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    @Basic
    @Column(name = "login_flags")
    public String getLoginFlags() {
        return loginFlags;
    }

    public void setLoginFlags(String loginFlags) {
        this.loginFlags = loginFlags;
    }

    @Basic
    @Column(name = "dept_id")
    public String getDeptId() {
        return deptId;
    }

    public void setDeptId(String deptId) {
        this.deptId = deptId;
    }

    @Basic
    @Column(name = "sex")
    public String getSex() {
        return sex;
    }

    public void setSex(String sex) {
        this.sex = sex;
    }
  
    @Basic
    @Column(name = "home_address")
    public String getHomeAddress() {
        return homeAddress;
    }
  
  	public void setHomeAddress(String homeAddress) {
        this.homeAddress = homeAddress;
    }

    @Basic
    @Column(name = "nation")
    public String getNation() {
        return nation;
    }

    public void setNation(String nation) {
        this.nation = nation;
    }

    @Basic
    @Column(name = "mobile")
    public String getMobile() {
        return mobile;
    }

    public void setMobile(String mobile) {
        this.mobile = mobile;
    }

    @Basic
    @Column(name = "tel")
    public String getTel() {
        return tel;
    }

    public void setTel(String tel) {
        this.tel = tel;
    }

    @Basic
    @Column(name = "email")
    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    @Basic
    @Column(name = "birth_date")
    public Timestamp getBirthDate() {
        return birthDate;
    }

    public void setBirthDate(Timestamp birthDate) {
        this.birthDate = birthDate;
    }

    @Basic
    @Column(name = "create_date")
    public Timestamp getCreateDate() {
        if (createDate==null){
            return new Timestamp(new Date().getTime());
        }else{
            return createDate;
        }
    }

    public void setCreateDate(Timestamp createDate) {
        if (createDate==null){
            this.createDate=new  Timestamp(new Date().getTime());
        }else{
            this.createDate = createDate;
        }
    }
    @Basic
    @Column(name = "modify_date")
    public Timestamp getModifyDate() {
        return modifyDate;
    }

    public void setModifyDate(Timestamp modifyDate) {
        this.modifyDate = modifyDate;
    }

    @Basic
    @Column(name = "practice_qualification_id")
    public String getPracticeQualificationId() {
        return practiceQualificationId;
    }

    public void setPracticeQualificationId(String practiceQualificationId) {
        this.practiceQualificationId = practiceQualificationId;
    }

    @Basic
    @Column(name = "extkey")
    public String getExtkey() {
        return extkey;
    }

    public void setExtkey(String extkey) {
        this.extkey = extkey;
    }

    @Basic
    @Column(name = "title")
    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    @Basic
    @Column(name = "research_direction")
    public String getResearchDirection() {
        return researchDirection;
    }

    public void setResearchDirection(String researchDirection) {
        this.researchDirection = researchDirection;
    }

    @Basic
    @Column(name = "signature")
    public String getSignature() {
        return signature;
    }

    public void setSignature(String signature) {
        this.signature = signature;
    }

    @Basic
    @Column(name = "picture")
    public String getPicture() {
        return picture;
    }

    public void setPicture(String picture) {
        this.picture = picture;
    }

    @Basic
    @Column(name = "rolename")
    public String getRolename() {
        return rolename;
    }

    public void setRolename(String rolename) {
        this.rolename = rolename;
    }


    public String getSalt() {
        return salt;
    }
    @Column(name="salt")
    public void setSalt(String salt) {
        this.salt = salt;
    }
    @Column(name="password")
    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }


    @Column(name="hospital_name")
    public String getHospitalName() {
        return hospitalName;
    }

    public void setHospitalName(String hospitalName) {
        this.hospitalName = hospitalName;
    }

    @Column(name="hospital_code")
    public String getHospitalCode() {
        return hospitalCode;
    }

    public void setHospitalCode(String hospitalCode) {
        this.hospitalCode = hospitalCode;
    }

    @Column(name="status")
    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        YunUsers yunUsers = (YunUsers) o;

        if (id != yunUsers.id) return false;
        if (userName != null ? !userName.equals(yunUsers.userName) : yunUsers.userName != null) return false;
        if (userId != null ? !userId.equals(yunUsers.userId) : yunUsers.userId != null) return false;
        if (loginFlags != null ? !loginFlags.equals(yunUsers.loginFlags) : yunUsers.loginFlags != null) return false;
        if (deptId != null ? !deptId.equals(yunUsers.deptId) : yunUsers.deptId != null) return false;
        if (sex != null ? !sex.equals(yunUsers.sex) : yunUsers.sex != null) return false;
        if (nation != null ? !nation.equals(yunUsers.nation) : yunUsers.nation != null) return false;
        if (mobile != null ? !mobile.equals(yunUsers.mobile) : yunUsers.mobile != null) return false;
        if (tel != null ? !tel.equals(yunUsers.tel) : yunUsers.tel != null) return false;
        if (email != null ? !email.equals(yunUsers.email) : yunUsers.email != null) return false;
        if (birthDate != null ? !birthDate.equals(yunUsers.birthDate) : yunUsers.birthDate != null) return false;
        if (createDate != null ? !createDate.equals(yunUsers.createDate) : yunUsers.createDate != null) return false;
        if (modifyDate != null ? !modifyDate.equals(yunUsers.modifyDate) : yunUsers.modifyDate != null) return false;
        if (practiceQualificationId != null ? !practiceQualificationId.equals(yunUsers.practiceQualificationId) : yunUsers.practiceQualificationId != null)
            return false;
        if (extkey != null ? !extkey.equals(yunUsers.extkey) : yunUsers.extkey != null) return false;
        if (title != null ? !title.equals(yunUsers.title) : yunUsers.title != null) return false;
        if (researchDirection != null ? !researchDirection.equals(yunUsers.researchDirection) : yunUsers.researchDirection != null)
            return false;
        if (signature != null ? !signature.equals(yunUsers.signature) : yunUsers.signature != null) return false;
        if (picture != null ? !picture.equals(yunUsers.picture) : yunUsers.picture != null) return false;
        if (rolename != null ? !rolename.equals(yunUsers.rolename) : yunUsers.rolename != null) return false;
        if (status != null ? !status.equals(yunUsers.status) : yunUsers.status != null) return false;

        return true;
    }


}